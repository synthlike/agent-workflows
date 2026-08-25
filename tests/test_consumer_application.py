from pathlib import Path
import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "skills/configure-workflows/references"
sys.path.insert(0, str(REFERENCES))
import application  # noqa: E402
import consumer  # noqa: E402
import lifecycle  # noqa: E402
import planning  # noqa: E402


TARGETS = {
    ".agents/workflows.yaml",
    "AGENTS.md",
    "docs/agents/workflows.md",
    "docs/agents/records.md",
    "docs/agents/backends/contract.py",
    "docs/agents/backends/local-markdown.md",
    "docs/agents/backends/local-markdown.py",
}


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def snapshot(root: Path) -> tuple[list[str], dict[str, bytes]]:
    return (
        sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_dir()),
        {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file()
        },
    )


def set_up_consumer(base: Path) -> tuple[Path, list[Path], dict]:
    root = base / "consumer"
    root.mkdir()
    manifest = lifecycle.generate_manifest(ROOT)
    skill_dirs = []
    for name in manifest["skills"]:
        target = root / ".agents/skills" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(ROOT / "skills" / name, target)
        skill_dirs.append(target)
    (root / "AGENTS.md").write_bytes(
        b"# Project-owned policy\r\n\r\nPreserve these exact bytes.\n"
    )
    return root, skill_dirs, manifest


def answers(root: Path) -> dict:
    expected = {path: None for path in TARGETS}
    for relative in expected:
        path = root / relative
        if path.is_file():
            expected[relative] = digest(path.read_bytes())
    return {
        "answer_version": 1,
        "selection": {"mode": "explicit", "skills": ["clarify-intent"]},
        "project": {
            "summary": "A local project shared by people and agents.",
            "documentation_style": "Keep documentation concise and explicit.",
        },
        "profile": {"name": "local-default", "local_backend": "local"},
        "backends": {"local": {"type": "local-markdown"}},
        "route_overrides": {},
        "consumer_state": {
            "root_guidance_path": "AGENTS.md",
            "expected_prior": dict(sorted(expected.items())),
        },
    }


def make_plan(root: Path, skill_dirs: list[Path], manifest: dict) -> dict:
    return planning.build_consumer_plan(root, skill_dirs, manifest, answers(root))


class FailedVerification:
    errors = ["injected verification failure"]

    def as_dict(self) -> dict:
        return {"errors": self.errors, "ok": False}


class ConsumerApplicationTests(unittest.TestCase):
    def test_successful_apply_writes_only_plan_and_verifies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs, manifest = set_up_consumer(Path(directory))
            plan = make_plan(root, skill_dirs, manifest)
            skill_snapshot = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for skill in skill_dirs for path in skill.rglob("*") if path.is_file()
            }
            parsed = application.parse_canonical_plan(
                planning.canonical_json(plan), plan["digest"]
            )
            result = application.apply_consumer_plan(root, parsed, manifest)
            self.assertTrue(result["ok"])
            self.assertEqual(sorted(TARGETS), result["files"])
            self.assertEqual(sorted(TARGETS), result["changed"])
            self.assertEqual([], result["verification"]["errors"])
            self.assertTrue(all(not (root / path).exists() for path in result["directories_left_absent"]))
            self.assertFalse((root / ".project").exists())
            self.assertEqual([], list(root.parent.glob(".agent-workflows-stage-*")))
            self.assertTrue((root / "AGENTS.md").read_bytes().startswith(
                b"# Project-owned policy\r\n\r\nPreserve these exact bytes.\n"
            ))
            self.assertEqual(
                skill_snapshot,
                {
                    path.relative_to(root).as_posix(): path.read_bytes()
                    for skill in skill_dirs for path in skill.rglob("*") if path.is_file()
                },
            )

    def test_stale_target_and_altered_plan_fail_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs, manifest = set_up_consumer(Path(directory))
            plan = make_plan(root, skill_dirs, manifest)
            (root / "AGENTS.md").write_bytes(b"changed after planning\n")
            before = snapshot(root)
            with self.assertRaisesRegex(application.ApplyError, "stale target state"):
                application.apply_consumer_plan(root, plan, manifest)
            self.assertEqual(before, snapshot(root))

            noncanonical = json.dumps(plan, sort_keys=True).encode()
            with self.assertRaisesRegex(application.ApplyError, "exact canonical JSON bytes"):
                application.parse_canonical_plan(noncanonical, plan["digest"])

            altered = copy.deepcopy(plan)
            target = next(item for item in altered["targets"] if item["kind"] == "text")
            target["content"] += "tampered\n"
            raw = planning.canonical_json(altered)
            with self.assertRaisesRegex(application.ApplyError, "plan digest is invalid"):
                application.parse_canonical_plan(raw, plan["digest"])
            self.assertEqual(before, snapshot(root))

    def test_recomputed_malicious_plan_is_rejected_by_complete_target_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs, manifest = set_up_consumer(Path(directory))
            plan = make_plan(root, skill_dirs, manifest)
            target = next(
                item for item in plan["targets"]
                if item["path"] == "docs/agents/workflows.md"
            )
            target["content"] += "malicious\n"
            target["destination_sha256"] = digest(target["content"].encode())
            body = dict(plan)
            del body["digest"]
            plan["digest"] = digest(planning.canonical_json(body))
            parsed = application.parse_canonical_plan(
                planning.canonical_json(plan), plan["digest"]
            )
            before = snapshot(root)
            with self.assertRaisesRegex(application.ApplyError, "differs from canonical rendering"):
                application.apply_consumer_plan(root, parsed, manifest)
            self.assertEqual(before, snapshot(root))

    def test_verification_failure_rolls_back_files_and_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs, manifest = set_up_consumer(Path(directory))
            plan = make_plan(root, skill_dirs, manifest)
            before = snapshot(root)
            with self.assertRaisesRegex(application.ApplyError, "rollback succeeded"):
                application.apply_consumer_plan(
                    root, plan, manifest,
                    verifier=lambda *_: FailedVerification(),
                )
            self.assertEqual(before, snapshot(root))

    def test_caught_write_failure_rolls_back(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs, manifest = set_up_consumer(Path(directory))
            plan = make_plan(root, skill_dirs, manifest)
            before = snapshot(root)
            calls = []

            def fail_after_first(relative: str) -> None:
                calls.append(relative)
                if len(calls) == 1:
                    raise OSError("injected write failure")

            with self.assertRaisesRegex(application.ApplyError, "rollback succeeded"):
                application.apply_consumer_plan(
                    root, plan, manifest, after_write=fail_after_first
                )
            self.assertEqual(before, snapshot(root))

    def test_replanned_identical_intent_applies_as_no_op(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs, manifest = set_up_consumer(Path(directory))
            first = make_plan(root, skill_dirs, manifest)
            application.apply_consumer_plan(root, first, manifest)
            second = make_plan(root, skill_dirs, manifest)
            before = snapshot(root)
            result = application.apply_consumer_plan(root, second, manifest)
            self.assertEqual([], result["changed"])
            self.assertEqual(sorted(TARGETS), result["unchanged"])
            self.assertEqual([], result["directories_created"])
            self.assertEqual(before, snapshot(root))

    def test_cli_requires_exact_digest_and_uses_plan_bound_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root, skill_dirs, manifest = set_up_consumer(base)
            plan = make_plan(root, skill_dirs, manifest)
            plan_path = base / "plan.json"
            plan_path.write_bytes(planning.canonical_json(plan))
            command = next(
                path for path in skill_dirs if path.name == "configure-workflows"
            ) / "references/lifecycle.py"
            wrong = subprocess.run(
                [
                    sys.executable, "-B", str(command), "apply-consumer",
                    "--consumer-root", str(root), "--plan", str(plan_path),
                    "--expected-digest", "sha256:" + "0" * 64,
                ],
                cwd=root, text=True, capture_output=True, check=False,
            )
            self.assertEqual(1, wrong.returncode)
            self.assertIn("does not match", wrong.stderr)
            self.assertFalse((root / ".agents/workflows.yaml").exists())

            completed = subprocess.run(
                [
                    sys.executable, "-B", str(command), "apply-consumer",
                    "--consumer-root", str(root), "--plan", str(plan_path),
                    "--expected-digest", plan["digest"],
                ],
                cwd=root, text=True, capture_output=True, check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            output = json.loads(completed.stdout)
            self.assertTrue(output["ok"])
            self.assertEqual(plan["digest"], output["digest"])
            verification = consumer.verify_consumer(root, skill_dirs, manifest)
            self.assertEqual([], verification.errors)


if __name__ == "__main__":
    unittest.main()
