from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "skills/configure-workflows/references"
sys.path.insert(0, str(REFERENCES))
import consumer  # noqa: E402
import lifecycle  # noqa: E402

sys.path.insert(0, str(ROOT / "tests"))
from consumer_fixture import copy_skills, write_guidance, write_schema2_config  # noqa: E402


MANIFEST = lifecycle.installed_manifest()
DISTRIBUTION_VERSION = MANIFEST["distribution"]["version"]


class InstalledLifecycleTests(unittest.TestCase):
    def set_up_consumer(
        self,
        base: Path,
        names: tuple[str, ...] | None = None,
        split_locations: bool = False,
        selected: tuple[str, ...] = ("clarify-intent",),
    ) -> tuple[Path, list[Path]]:
        root = base / "consumer"
        root.mkdir()
        names = names or tuple(MANIFEST["skills"])
        skill_dirs = copy_skills(
            ROOT,
            root,
            names,
            split_locations=split_locations,
        )
        inventory = {
            path.name: path.relative_to(root).as_posix() for path in skill_dirs
        }
        write_schema2_config(root, MANIFEST["distribution"], selected, inventory)
        write_guidance(root)
        return root, skill_dirs

    def verify(self, root: Path, skill_dirs: list[Path]) -> consumer.Verification:
        return consumer.verify_consumer(root, skill_dirs, lifecycle.installed_manifest())

    def test_verifies_schema_2_across_several_discovered_locations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory), split_locations=True)
            result = self.verify(root, skill_dirs)
            self.assertEqual([], result.errors)
            self.assertEqual(["clarify-intent", "configure-workflows"], result.closure)
            self.assertEqual(sorted(MANIFEST["skills"]), result.installed)

    def test_copied_lifecycle_verifies_without_source_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory), split_locations=True)
            command = next(path for path in skill_dirs if path.name == "configure-workflows") / "references/lifecycle.py"
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
            self.assertEqual(DISTRIBUTION_VERSION, output["release"])
            self.assertEqual(["clarify-intent", "configure-workflows"], output["closure"])

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
                names=("configure-workflows", "develop-rfc"),
                selected=("develop-rfc",),
            )
            errors = self.verify(root, skill_dirs).errors
            self.assertTrue(any("complete distribution is missing installed skills" in error for error in errors))
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
                    "    clarify-intent: .skills/configure-workflows",
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
            config.write_text(config.read_text().replace(DISTRIBUTION_VERSION, "latest"))
            errors = self.verify(root, skill_dirs).errors
            self.assertIn("distribution.version must be immutable", errors)
            self.assertIn("configured distribution identity does not match installed manifest", errors)

        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            config.write_text(config.read_text().replace(DISTRIBUTION_VERSION, "v9.9.9"))
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
                    path for path in skill_dirs if path.name == "configure-workflows"
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

    def test_verifies_github_backend_assets_and_rejects_unknown_backends(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            config.write_text(
                config.read_text().replace(
                    "backend: local-markdown",
                    "backend: github\n  login: octocat",
                )
            )
            (root / "docs/agents/issue-tracker.md").write_text(
                (REFERENCES / "issue-tracker-github.md").read_text()
            )
            (root / "docs/agents/github-issues.py").write_text(
                (REFERENCES / "github-issues.py").read_text()
            )
            self.assertEqual([], self.verify(root, skill_dirs).errors)
            config.write_text(config.read_text().replace("  login: octocat\n", ""))
            self.assertIn(
                "issue_tracker.login is required for the GitHub backend",
                self.verify(root, skill_dirs).errors,
            )
            config.write_text(
                config.read_text().replace(
                    "backend: github\n", "backend: github\n  login: octocat\n"
                )
            )
            helper = root / "docs/agents/github-issues.py"
            helper.write_text(helper.read_text() + "\n# local change\n")
            self.assertIn(
                "GitHub backend helper does not match the installed helper",
                self.verify(root, skill_dirs).errors,
            )
            helper.unlink()
            self.assertIn(
                "missing required GitHub backend helper: docs/agents/github-issues.py",
                self.verify(root, skill_dirs).errors,
            )

        with tempfile.TemporaryDirectory() as directory:
            root, skill_dirs = self.set_up_consumer(Path(directory))
            config = root / ".agents/workflows.yaml"
            config.write_text(
                config.read_text().replace("backend: local-markdown", "backend: bear")
            )
            self.assertIn(
                "unsupported issue_tracker.backend: bear",
                self.verify(root, skill_dirs).errors,
            )

    def test_rejects_duplicate_selected_values_and_unsupported_schema(self) -> None:
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
            config.write_text(config.read_text().replace("schema_version: 2", "schema_version: 999"))
            self.assertIn("schema_version must be 2", self.verify(root, skill_dirs).errors)


if __name__ == "__main__":
    unittest.main()
