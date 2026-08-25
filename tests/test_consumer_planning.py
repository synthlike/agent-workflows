from pathlib import Path
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "skills/configure-workflows/references"
sys.path.insert(0, str(REFERENCES))
import lifecycle  # noqa: E402
import planning  # noqa: E402
import templates  # noqa: E402


TEXT_TARGETS = {
    ".agents/workflows.yaml",
    "AGENTS.md",
    "docs/agents/workflows.md",
    "docs/agents/records.md",
}
LOCAL_ASSETS = {
    "docs/agents/backends/contract.py",
    "docs/agents/backends/local-markdown.md",
    "docs/agents/backends/local-markdown.py",
}
GITHUB_ASSETS = {
    "docs/agents/backends/github.md",
    "docs/agents/backends/github.py",
}


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def snapshot(root: Path) -> tuple[list[str], dict[str, bytes]]:
    directories = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_dir()
    )
    files = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
    return directories, files


class ConsumerPlanningTests(unittest.TestCase):
    def set_up_consumer(self, base: Path) -> tuple[Path, list[Path], dict]:
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
            b"# Consumer policy\r\n\r\nThese bytes belong to the project.\n"
        )
        return root, skill_dirs, manifest

    def answers(
        self,
        root: Path,
        *,
        explicit: bool = False,
        github_issues: bool = False,
    ) -> dict:
        backends = {"local": {"type": "local-markdown"}}
        overrides: dict[str, dict] = {}
        assets = set(LOCAL_ASSETS)
        if github_issues:
            backends["github"] = {
                "type": "github",
                "repository": "acme/project",
                "login": "octocat",
            }
            overrides["issues"] = {
                "backend": "github",
                "destination": {"label": "workflow:record:issues"},
            }
            assets.update(GITHUB_ASSETS)
        targets = TEXT_TARGETS | assets
        expected = {path: None for path in targets}
        expected["AGENTS.md"] = digest((root / "AGENTS.md").read_bytes())
        return {
            "answer_version": 1,
            "selection": (
                {"mode": "explicit", "skills": ["research-question", "clarify-intent"]}
                if explicit else {"mode": "all"}
            ),
            "project": {
                "summary": "A shared project configured by people and coding agents.",
                "documentation_style": "Use the established concise project style.",
            },
            "profile": {"name": "local-default", "local_backend": "local"},
            "backends": backends,
            "route_overrides": overrides,
            "consumer_state": {
                "root_guidance_path": "AGENTS.md",
                "expected_prior": dict(sorted(expected.items())),
            },
        }

    def test_plan_is_deterministic_complete_and_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs, manifest = self.set_up_consumer(Path(directory))
            answer = self.answers(root)
            before = snapshot(root)
            first = planning.build_consumer_plan(root, skill_dirs, manifest, answer)
            second = planning.build_consumer_plan(root, list(reversed(skill_dirs)), manifest, answer)
            self.assertEqual(first, second)
            self.assertEqual(before, snapshot(root))

            without_digest = dict(first)
            del without_digest["digest"]
            self.assertEqual(digest(planning.canonical_json(without_digest)), first["digest"])
            self.assertEqual(1, first["plan_version"])
            self.assertEqual(
                digest(planning.canonical_json(manifest)),
                first["distribution"]["manifest_sha256"],
            )
            self.assertEqual(set(manifest["skills"]), set(first["installation"]["skills"]))
            self.assertNotIn("configure-workflows", first["installation"]["selected"])
            self.assertIn("configure-workflows", first["installation"]["closure"])
            self.assertEqual(TEXT_TARGETS | LOCAL_ASSETS, {t["path"] for t in first["targets"]})
            self.assertIn("docs/agents/backends", first["directories_to_create"])
            self.assertIn(".project", first["directories_left_absent"])
            self.assertIn("docs/domain", first["directories_left_absent"])

            target_by_path = {target["path"]: target for target in first["targets"]}
            self.assertEqual("text", target_by_path[".agents/workflows.yaml"]["kind"])
            self.assertIn(
                "A shared project configured by people and coding agents.",
                target_by_path["docs/agents/workflows.md"]["content"],
            )
            self.assertIn(
                "# Consumer policy\r\n\r\nThese bytes belong to the project.\n",
                target_by_path["AGENTS.md"]["content"],
            )
            for path in LOCAL_ASSETS:
                target = target_by_path[path]
                self.assertEqual("copy", target["kind"])
                self.assertEqual(target["source"]["sha256"], target["destination_sha256"])

    def test_explicit_selection_named_backends_and_route_override(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs, manifest = self.set_up_consumer(Path(directory))
            plan = planning.build_consumer_plan(
                root, skill_dirs, manifest,
                self.answers(root, explicit=True, github_issues=True),
            )
            self.assertEqual(
                ["clarify-intent", "research-question"],
                plan["installation"]["selected"],
            )
            self.assertEqual("github", plan["intent"]["records"]["issues"]["backend"])
            self.assertEqual(
                TEXT_TARGETS | LOCAL_ASSETS | GITHUB_ASSETS,
                {target["path"] for target in plan["targets"]},
            )

    def test_rejects_stale_malformed_unsupported_escaping_and_colliding_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs, manifest = self.set_up_consumer(Path(directory))
            valid = self.answers(root)
            cases = []
            stale = copy.deepcopy(valid)
            stale["consumer_state"]["expected_prior"]["AGENTS.md"] = None
            cases.append((stale, "stale consumer state"))
            malformed = copy.deepcopy(valid)
            malformed["unexpected"] = True
            cases.append((malformed, "must contain exactly"))
            unsupported = copy.deepcopy(valid)
            unsupported["profile"]["name"] = "magic"
            cases.append((unsupported, "must be local-default"))
            malformed_backend = copy.deepcopy(valid)
            malformed_backend["backends"]["github"] = {
                "type": "github", "repository": "not-a-repository", "login": "octocat"
            }
            cases.append((malformed_backend, "must use OWNER/REPO form"))
            escaping = copy.deepcopy(valid)
            escaping["consumer_state"]["root_guidance_path"] = "../AGENTS.md"
            cases.append((escaping, "normalized relative path"))
            colliding = copy.deepcopy(valid)
            colliding["route_overrides"]["domain"] = {
                "destination": {"path": "docs/agents"}
            }
            cases.append((colliding, "collides with managed output"))
            incomplete = copy.deepcopy(valid)
            del incomplete["consumer_state"]["expected_prior"]["docs/agents/records.md"]
            cases.append((incomplete, "target mismatch"))
            before = snapshot(root)
            for answer, message in cases:
                with self.subTest(message=message):
                    with self.assertRaisesRegex(planning.PlanError, message):
                        planning.build_consumer_plan(root, skill_dirs, manifest, answer)
                    self.assertEqual(before, snapshot(root))

    def test_installed_cli_is_source_checkout_free_and_invokes_no_provider_tools(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root, skill_dirs, _ = self.set_up_consumer(base)
            answers_path = base / "answers.json"
            answers_path.write_text(json.dumps(self.answers(root)))
            binary_dir = base / "bin"
            binary_dir.mkdir()
            markers = []
            for name in ("gh", "bearcli"):
                marker = base / f"{name}.called"
                markers.append(marker)
                executable = binary_dir / name
                executable.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 99\n")
                executable.chmod(0o755)
            command = next(path for path in skill_dirs if path.name == "configure-workflows") / "references/lifecycle.py"
            environment = dict(os.environ)
            environment["PATH"] = str(binary_dir) + os.pathsep + environment.get("PATH", "")
            arguments = [
                sys.executable, "-B", str(command), "plan-consumer",
                "--consumer-root", str(root),
                "--skills-root", str(root / ".agents/skills"),
                "--answers", str(answers_path),
            ]
            before = snapshot(root)
            first = subprocess.run(
                arguments, cwd=root, env=environment, text=True,
                capture_output=True, check=False,
            )
            second = subprocess.run(
                arguments, cwd=root, env=environment, text=True,
                capture_output=True, check=False,
            )
            self.assertEqual(0, first.returncode, first.stderr)
            self.assertEqual(first.stdout, second.stdout)
            self.assertEqual(before, snapshot(root))
            self.assertTrue(all(not marker.exists() for marker in markers))
            plan = json.loads(first.stdout)
            self.assertTrue(planning.DIGEST.fullmatch(plan["digest"]))

    def test_answer_schema_is_strict_and_versioned(self) -> None:
        schema = json.loads((REFERENCES / "consumer-answers.schema.json").read_text())
        self.assertEqual(False, schema["additionalProperties"])
        self.assertEqual({"const": 1}, schema["properties"]["answer_version"])
        self.assertEqual("local-default", schema["properties"]["profile"]["properties"]["name"]["const"])
        self.assertEqual(False, schema["properties"]["route_overrides"]["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
