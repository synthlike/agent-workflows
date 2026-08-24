from pathlib import Path
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
import lifecycle  # noqa: E402


POINTERS = """# Agent guidance

Workflow configuration is in `.agents/workflows.yaml`. Before significant design or planning work, read `docs/agents/workflows.md`. Perform issue operations according to `docs/agents/issue-tracker.md`.
"""


class InstalledLifecycleTests(unittest.TestCase):
    def set_up_consumer(
        self,
        base: Path,
        names: tuple[str, ...] = ("configure-project", "clarify-intent"),
        split_locations: bool = False,
        selected: tuple[str, ...] = ("clarify-intent",),
    ) -> tuple[Path, list[Path]]:
        root = base / "consumer"
        root.mkdir()
        skill_dirs = []
        inventory: dict[str, str] = {}
        for index, name in enumerate(names):
            parent = root / (f"location-{index}" if split_locations else ".skills")
            parent.mkdir(parents=True, exist_ok=True)
            target = parent / name
            shutil.copytree(ROOT / "skills" / name, target)
            skill_dirs.append(target)
            inventory[name] = target.relative_to(root).as_posix()
        (root / ".agents").mkdir()
        selected_lines = "\n".join(f"    - {name}" for name in selected)
        skill_lines = "\n".join(f"    {name}: {path}" for name, path in sorted(inventory.items()))
        (root / ".agents/workflows.yaml").write_text(
            f"""schema_version: 2

distribution:
  source: github.com/synthlike/agent-workflows
  version: v0.2.0

installation:
  selected:
{selected_lines}
  skills:
{skill_lines}

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
        (root / "docs/agents").mkdir(parents=True)
        (root / "docs/agents/workflows.md").write_text("# Workflows\n")
        (root / "docs/agents/issue-tracker.md").write_text("# Local Markdown\n")
        (root / "AGENTS.md").write_text(POINTERS)
        return root, skill_dirs

    def verify(self, root: Path, skill_dirs: list[Path]) -> consumer.Verification:
        return consumer.verify_consumer(root, skill_dirs, lifecycle.installed_manifest())

    def test_verifies_schema_2_across_several_discovered_locations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory), split_locations=True)
            result = self.verify(root, skill_dirs)
            self.assertEqual([], result.errors)
            self.assertEqual(["clarify-intent", "configure-project"], result.closure)
            self.assertEqual(["clarify-intent", "configure-project"], result.installed)

    def test_copied_lifecycle_verifies_without_source_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory), split_locations=True)
            command = next(path for path in skill_dirs if path.name == "configure-project") / "references/lifecycle.py"
            invocation = [
                sys.executable,
                "-B",
                str(command),
                "verify-consumer",
                "--consumer-root",
                str(root),
            ]
            for path in skill_dirs:
                invocation.extend(("--skill-dir", str(path)))
            invocation.append("--json")
            completed = subprocess.run(
                invocation,
                cwd=Path(directory),
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            output = json.loads(completed.stdout)
            self.assertTrue(output["ok"])
            self.assertEqual("v0.2.0", output["release"])
            self.assertEqual(["clarify-intent", "configure-project"], output["closure"])

    def test_manifest_closure_inspection_and_verification_have_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            command = REFERENCES / "lifecycle.py"
            cases = (
                (["show-manifest", "--json"], "manifest_version"),
                (["closure", "clarify-intent", "--json"], "closure"),
                (
                    [
                        "inspect",
                        "--consumer-root",
                        str(root),
                        "--skills-root",
                        str(skill_dirs[0].parent),
                        "--json",
                    ],
                    "installed",
                ),
                (
                    [
                        "verify-consumer",
                        "--consumer-root",
                        str(root),
                        "--skills-root",
                        str(skill_dirs[0].parent),
                        "--json",
                    ],
                    "selected",
                ),
            )
            for arguments, expected_key in cases:
                with self.subTest(arguments=arguments):
                    completed = subprocess.run(
                        [sys.executable, "-B", str(command), *arguments],
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(0, completed.returncode, completed.stderr)
                    self.assertIn(expected_key, json.loads(completed.stdout))

    def test_rejects_unknown_selection_and_incomplete_closure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory), selected=("unknown-skill",))
            self.assertIn(
                "unknown selected skills: unknown-skill",
                self.verify(root, skill_dirs).errors,
            )

        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(
                Path(directory),
                names=("configure-project", "develop-rfc"),
                selected=("develop-rfc",),
            )
            errors = self.verify(root, skill_dirs).errors
            self.assertTrue(any("missing installed dependencies" in error for error in errors))
            self.assertTrue(any("selected workflow closure is incomplete" in error for error in errors))

    def test_rejects_stale_and_duplicate_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            text = config.read_text().replace(
                "    clarify-intent: .skills/clarify-intent\n",
                "    stale-skill: .skills/stale-skill\n",
            )
            config.write_text(text)
            errors = self.verify(root, skill_dirs).errors
            self.assertTrue(any("unknown skills: stale-skill" in error for error in errors))
            self.assertTrue(any("missing discovered skills: clarify-intent" in error for error in errors))
            self.assertTrue(any("stale skills: stale-skill" in error for error in errors))

        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            config.write_text(
                config.read_text().replace(
                    "    clarify-intent: .skills/clarify-intent",
                    "    clarify-intent: .skills/configure-project",
                )
            )
            errors = self.verify(root, skill_dirs).errors
            self.assertTrue(any("wrong directory name" in error for error in errors))
            self.assertTrue(any("path collision" in error for error in errors))

    def test_rejects_escaping_and_discovery_mismatched_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            config.write_text(
                config.read_text().replace(
                    "    clarify-intent: .skills/clarify-intent",
                    "    clarify-intent: ../clarify-intent",
                )
            )
            self.assertTrue(any("escapes the consumer root" in error for error in self.verify(root, skill_dirs).errors))

        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            other = root / "other/clarify-intent"
            other.parent.mkdir()
            config.write_text(
                config.read_text().replace(
                    "    clarify-intent: .skills/clarify-intent",
                    "    clarify-intent: other/clarify-intent",
                )
            )
            self.assertTrue(any("does not match harness discovery" in error for error in self.verify(root, skill_dirs).errors))

    def test_rejects_mutable_or_mismatched_distribution_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            config.write_text(config.read_text().replace("v0.2.0", "latest"))
            errors = self.verify(root, skill_dirs).errors
            self.assertIn("distribution.version must be immutable", errors)
            self.assertIn("configured distribution identity does not match installed manifest", errors)

        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            config.write_text(config.read_text().replace("v0.2.0", "v0.2.1"))
            self.assertIn(
                "configured distribution identity does not match installed manifest",
                self.verify(root, skill_dirs).errors,
            )

    def test_distinguishes_missing_extra_and_modified_files_without_mutation(self) -> None:
        cases = ("missing", "extra", "modified")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root, skill_dirs = self.set_up_consumer(Path(directory))
                target = next(path for path in skill_dirs if path.name == "clarify-intent")
                if case == "missing":
                    (target / "SKILL.md").unlink()
                elif case == "extra":
                    (target / "extra.md").write_text("extra\n")
                else:
                    (target / "SKILL.md").write_text((target / "SKILL.md").read_text() + "\nchanged\n")
                before = {path.relative_to(target): path.read_bytes() for path in target.rglob("*") if path.is_file()}
                errors = self.verify(root, skill_dirs).errors
                after = {path.relative_to(target): path.read_bytes() for path in target.rglob("*") if path.is_file()}
                self.assertTrue(any(case in error for error in errors), errors)
                self.assertEqual(before, after)

    def test_rejects_missing_or_mismatched_installed_manifest(self) -> None:
        for case in ("missing", "mismatched"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                root, skill_dirs = self.set_up_consumer(Path(directory))
                manifest = next(
                    path for path in skill_dirs if path.name == "configure-project"
                ) / "references/distribution-manifest.json"
                if case == "missing":
                    manifest.unlink()
                else:
                    manifest.write_text("{}\n")
                errors = self.verify(root, skill_dirs).errors
                self.assertTrue(
                    any(case in error and "distribution manifest" in error for error in errors),
                    errors,
                )

    def test_rejects_broken_internal_reference_and_missing_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            target = next(path for path in skill_dirs if path.name == "clarify-intent") / "SKILL.md"
            target.write_text(target.read_text() + "\n[Missing](references/nope.md)\n")
            (root / "docs/agents/issue-tracker.md").unlink()
            errors = self.verify(root, skill_dirs).errors
            self.assertTrue(any("broken relative reference" in error for error in errors))
            self.assertIn("missing required guidance: docs/agents/issue-tracker.md", errors)

    def test_rejects_duplicate_selected_values_and_schema_1(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            config.write_text(
                config.read_text().replace(
                    "    - clarify-intent",
                    "    - clarify-intent\n    - clarify-intent",
                )
            )
            self.assertIn(
                "installation.selected must contain unique skill names",
                self.verify(root, skill_dirs).errors,
            )

        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            config.write_text(config.read_text().replace("schema_version: 2", "schema_version: 1"))
            self.assertIn("schema_version must be 2", self.verify(root, skill_dirs).errors)


if __name__ == "__main__":
    unittest.main()
