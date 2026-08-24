from pathlib import Path
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "skills/configure-project/references"
sys.path.insert(0, str(REFERENCES))
import consumer  # noqa: E402
import fresh_install  # noqa: E402
import lifecycle  # noqa: E402


class FreshInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = lifecycle.installed_manifest()
        cls.bundle = lifecycle.validate_bundle_bytes(lifecycle.build_bundle(ROOT))

    def initial_consumer(
        self,
        base: Path,
        installed: tuple[str, ...] = ("configure-project",),
        fixture: str | None = None,
    ) -> tuple[Path, list[Path]]:
        root = base / "consumer"
        if fixture:
            shutil.copytree(ROOT / "tests/fixtures" / fixture, root)
        else:
            root.mkdir()
        skill_root = root / ".claude/skills"
        skill_root.mkdir(parents=True)
        paths = []
        for name in installed:
            target = skill_root / name
            shutil.copytree(ROOT / "skills" / name, target)
            paths.append(target)
        return root, paths

    def plan(
        self,
        root: Path,
        paths: list[Path],
        selected: set[str] | None = None,
        overrides: dict[str, Path] | None = None,
    ) -> dict:
        return fresh_install.plan_fresh_install(
            root,
            paths,
            selected or {"clarify-intent"},
            self.manifest,
            self.bundle,
            overrides,
        )

    def configure_from_plan(self, root: Path, plan: dict) -> None:
        fragment = plan["configuration"]
        selected = "\n".join(f"    - {name}" for name in fragment["installation"]["selected"])
        skills = "\n".join(
            f"    {name}: {path}"
            for name, path in sorted(fragment["installation"]["skills"].items())
        )
        (root / ".agents").mkdir(exist_ok=True)
        (root / ".agents/workflows.yaml").write_text(
            f"""schema_version: 2

distribution:
  source: {fragment['distribution']['source']}
  version: {fragment['distribution']['version']}

installation:
  selected:
{selected}
  skills:
{skills}

issue_tracker:
  backend: local-markdown
  root: .project

artifacts:
  domain: {{enabled: true, path: docs/domain}}
  arps: {{enabled: true, path: docs/decisions, prefix: ARP}}
  rfcs: {{enabled: true, path: docs/rfcs, prefix: RFC}}
  meetings: {{enabled: false, path: docs/meetings}}
  specifications: {{enabled: true, path: docs/specifications}}
"""
        )
        (root / "docs/agents").mkdir(parents=True, exist_ok=True)
        (root / "docs/agents/workflows.md").write_text("# Workflows\n")
        (root / "docs/agents/issue-tracker.md").write_text("# Local Markdown\n")
        agents = root / "AGENTS.md"
        original = agents.read_text() if agents.exists() else "# Agent guidance\n"
        agents.write_text(
            original.rstrip()
            + "\n\nWorkflow configuration is in `.agents/workflows.yaml`. "
            + "Read `docs/agents/workflows.md` and `docs/agents/issue-tracker.md`.\n"
        )

    def test_plan_reports_complete_dry_run_and_default_destination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, paths = self.initial_consumer(Path(directory))
            plan = self.plan(root, paths)
            self.assertEqual([], plan["errors"])
            self.assertEqual(["clarify-intent", "configure-project"], plan["closure"])
            self.assertEqual(["clarify-intent"], plan["missing"])
            self.assertEqual([], plan["unexpected"])
            action = plan["actions"][0]
            self.assertEqual(".claude/skills/clarify-intent", action["destination"])
            self.assertEqual("skills/clarify-intent", action["source"])
            self.assertTrue(action["files"])
            self.assertEqual(self.bundle.digest, plan["bundle_sha256"])
            self.assertEqual(2, plan["configuration"]["schema_version"])
            self.assertEqual(
                ".claude/skills/clarify-intent",
                plan["configuration"]["installation"]["skills"]["clarify-intent"],
            )
            self.assertEqual(64, len(plan["plan_id"]))

    def test_plan_supports_repository_contained_destination_override(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, paths = self.initial_consumer(Path(directory))
            plan = self.plan(
                root,
                paths,
                overrides={"clarify-intent": Path(".agents/skills/clarify-intent")},
            )
            self.assertEqual([], plan["errors"])
            self.assertEqual(
                ".agents/skills/clarify-intent",
                plan["actions"][0]["destination"],
            )

    def test_plan_reports_unexpected_duplicate_modified_and_incomplete_skills(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, paths = self.initial_consumer(
                Path(directory),
                installed=("configure-project", "prepare-handoff"),
            )
            plan = self.plan(root, paths)
            self.assertEqual(["prepare-handoff"], plan["unexpected"])
            self.assertEqual([], plan["errors"])

            duplicate = self.plan(root, [*paths, paths[-1]])
            self.assertTrue(any("duplicated" in error for error in duplicate["errors"]))

            target = paths[-1] / "SKILL.md"
            target.write_text(target.read_text() + "\nmodified\n")
            modified = self.plan(root, paths)
            self.assertTrue(any("modified distributed file" in error for error in modified["errors"]))

            target.unlink()
            incomplete = self.plan(root, paths)
            self.assertTrue(any("missing distributed file" in error for error in incomplete["errors"]))

    def test_plan_blocks_occupied_escaping_wrong_and_unknown_overrides(self) -> None:
        cases = (
            ({"clarify-intent": Path(".claude/skills/clarify-intent")}, "occupied"),
            ({"clarify-intent": Path("../clarify-intent")}, "escapes"),
            ({"clarify-intent": Path(".skills/wrong-name")}, "wrong directory name"),
            ({"configure-project": Path(".skills/configure-project")}, "not missing"),
        )
        for overrides, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as directory:
                root, paths = self.initial_consumer(Path(directory))
                if expected == "occupied":
                    (root / ".claude/skills/clarify-intent").mkdir()
                plan = self.plan(root, paths, overrides=overrides)
                self.assertTrue(any(expected in error for error in plan["errors"]), plan["errors"])

    def test_apply_creates_only_missing_skills_and_rechecks_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, paths = self.initial_consumer(Path(directory))
            configure_before = {
                path.relative_to(paths[0]): path.read_bytes()
                for path in paths[0].rglob("*")
                if path.is_file()
            }
            plan = self.plan(root, paths)
            created = fresh_install.apply_fresh_install(
                plan,
                root,
                self.bundle,
                self.manifest,
            )
            self.assertEqual([".claude/skills/clarify-intent"], created)
            self.assertFalse((root / ".agents/workflows.yaml").exists())
            configure_after = {
                path.relative_to(paths[0]): path.read_bytes()
                for path in paths[0].rglob("*")
                if path.is_file()
            }
            self.assertEqual(configure_before, configure_after)
            self.assertTrue((root / created[0] / "SKILL.md").is_file())

            with self.assertRaisesRegex(fresh_install.FreshInstallError, "inputs changed"):
                fresh_install.apply_fresh_install(plan, root, self.bundle, self.manifest)

    def test_apply_rejects_tampered_plan_bundle_or_current_skills(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, paths = self.initial_consumer(Path(directory))
            plan = self.plan(root, paths)
            tampered = copy.deepcopy(plan)
            tampered["selected"] = ["research-question"]
            with self.assertRaisesRegex(fresh_install.FreshInstallError, "identity is invalid"):
                fresh_install.apply_fresh_install(tampered, root, self.bundle, self.manifest)

            changed_bundle = copy.copy(self.bundle)
            object.__setattr__(changed_bundle, "digest", "0" * 64)
            with self.assertRaisesRegex(fresh_install.FreshInstallError, "bundle changed"):
                fresh_install.apply_fresh_install(plan, root, changed_bundle, self.manifest)

            skill = paths[0] / "SKILL.md"
            skill.write_text(skill.read_text() + "\nchanged\n")
            with self.assertRaisesRegex(fresh_install.FreshInstallError, "inputs changed"):
                fresh_install.apply_fresh_install(plan, root, self.bundle, self.manifest)

    def test_failure_before_first_publish_leaves_no_visible_skill(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, paths = self.initial_consumer(Path(directory))
            plan = self.plan(root, paths)

            def fail(_name: str, _destination: Path) -> None:
                raise RuntimeError("injected")

            with self.assertRaisesRegex(
                fresh_install.FreshInstallError,
                "created skill directories requiring cleanup: none",
            ):
                fresh_install.apply_fresh_install(
                    plan,
                    root,
                    self.bundle,
                    self.manifest,
                    before_publish=fail,
                )
            self.assertFalse((root / ".claude/skills/clarify-intent").exists())
            self.assertEqual([], list((root / ".claude/skills").glob(".*agent-workflows-stage-*")))

    def test_failure_after_publication_reports_exact_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, paths = self.initial_consumer(Path(directory))
            plan = self.plan(root, paths, selected={"record-arp"})
            calls = 0

            def fail_second(_name: str, _destination: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise RuntimeError("injected")

            with self.assertRaisesRegex(
                fresh_install.FreshInstallError,
                "created skill directories requiring cleanup: ",
            ) as caught:
                fresh_install.apply_fresh_install(
                    plan,
                    root,
                    self.bundle,
                    self.manifest,
                    before_publish=fail_second,
                )
            created = str(caught.exception).split("cleanup: ", 1)[1]
            self.assertNotEqual("none", created)
            self.assertTrue((root / created).is_dir())
            stages = list((root / ".claude/skills").glob(".*agent-workflows-stage-*"))
            self.assertEqual([], stages)

    def test_empty_and_existing_projects_remain_lazy_and_verify_after_confirmation(self) -> None:
        for fixture in ("empty-project", "existing-project"):
            with self.subTest(fixture=fixture), tempfile.TemporaryDirectory() as directory:
                root, paths = self.initial_consumer(Path(directory), fixture=fixture)
                original_context = (root / "CONTEXT.md").read_bytes() if (root / "CONTEXT.md").exists() else None
                plan = self.plan(root, paths)
                fresh_install.apply_fresh_install(plan, root, self.bundle, self.manifest)
                discovered = sorted(path for path in (root / ".claude/skills").iterdir() if path.is_dir())
                self.configure_from_plan(root, plan)
                result = consumer.verify_consumer(root, discovered, self.manifest)
                self.assertEqual([], result.errors)
                if original_context is not None:
                    self.assertEqual(original_context, (root / "CONTEXT.md").read_bytes())
                for optional in (
                    ".project",
                    "docs/domain",
                    "docs/decisions",
                    "docs/rfcs",
                    "docs/meetings",
                    "docs/specifications",
                ):
                    self.assertFalse((root / optional).exists())

    def test_cli_plan_and_apply_require_harness_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            root, paths = self.initial_consumer(temporary)
            bundle_path = temporary / "bundle.tar.gz"
            plan_path = temporary / "plan.json"
            bundle_path.write_bytes(lifecycle.build_bundle(ROOT))
            command = paths[0] / "references/lifecycle.py"
            plan = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(command),
                    "plan-fresh",
                    str(bundle_path),
                    "--consumer-root",
                    str(root),
                    "--skills-root",
                    str(paths[0].parent),
                    "--selected",
                    "clarify-intent",
                    "--output",
                    str(plan_path),
                    "--json",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, plan.returncode, plan.stderr)
            self.assertEqual(json.loads(plan.stdout), json.loads(plan_path.read_text()))
            apply = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(command),
                    "apply-fresh",
                    str(bundle_path),
                    "--consumer-root",
                    str(root),
                    "--plan",
                    str(plan_path),
                    "--json",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, apply.returncode, apply.stderr)
            result = json.loads(apply.stdout)
            self.assertTrue(result["requires_harness_discovery_confirmation"])
            self.assertFalse((root / ".agents/workflows.yaml").exists())


if __name__ == "__main__":
    unittest.main()
