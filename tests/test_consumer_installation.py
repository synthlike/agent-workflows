from pathlib import Path
import shutil
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_consumer_installation import verify  # noqa: E402


CONFIG = """schema_version: 1

distribution:
  source: github.com/synthlike/agent-workflows
  version: e9d7dbb926931e2c7970e547fdb42b9906bb4cab

issue_tracker:
  backend: local-markdown
  root: .project

artifacts:
  domain:
    enabled: true
    path: docs/domain
  arps:
    enabled: true
    path: docs/decisions
    prefix: ARP
  rfcs:
    enabled: true
    path: docs/rfcs
    prefix: RFC
  meetings:
    enabled: false
    path: docs/meetings
  specifications:
    enabled: true
    path: docs/specifications
"""

POINTERS = """
## Engineering workflows

Workflow configuration is in `.agents/workflows.yaml`. Before significant design or planning work, read `docs/agents/workflows.md`. Perform issue operations according to `docs/agents/issue-tracker.md`.
"""


class ConsumerInstallationTests(unittest.TestCase):
    def configure(self, consumer: Path) -> None:
        (consumer / ".agents").mkdir(parents=True)
        (consumer / ".agents/workflows.yaml").write_text(CONFIG)
        (consumer / "docs/agents").mkdir(parents=True)
        (consumer / "docs/agents/workflows.md").write_text("# Workflows\n")
        (consumer / "docs/agents/issue-tracker.md").write_text("# Local Markdown\n")
        agents = consumer / "AGENTS.md"
        existing = agents.read_text() if agents.exists() else "# Agent guidance\n"
        agents.write_text(existing.rstrip() + "\n" + POINTERS)

    def install_skills(self, destination: Path) -> list[Path]:
        destination.mkdir(parents=True)
        installed = []
        for source in sorted((ROOT / "skills").iterdir()):
            if source.is_dir():
                target = destination / source.name
                shutil.copytree(source, target)
                installed.append(target)
        return installed

    def verify(self, consumer: Path, skills: list[Path]) -> list[str]:
        return verify(
            consumer,
            skills,
            ROOT / "skills",
            ROOT / "docs/workflow-dependencies.md",
        )

    def test_fresh_project_writes_only_declared_setup_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            consumer = temporary / "consumer"
            shutil.copytree(ROOT / "tests/fixtures/empty-project", consumer)
            before = {path.relative_to(consumer) for path in consumer.rglob("*") if path.is_file()}
            self.configure(consumer)
            skills = self.install_skills(temporary / "harness/discovered")
            after = {path.relative_to(consumer) for path in consumer.rglob("*") if path.is_file()}
            self.assertEqual(
                {
                    Path(".agents/workflows.yaml"),
                    Path("AGENTS.md"),
                    Path("docs/agents/issue-tracker.md"),
                    Path("docs/agents/workflows.md"),
                },
                after - before,
            )
            for optional in (".project", "docs/domain", "docs/decisions", "docs/rfcs", "docs/meetings", "docs/specifications"):
                self.assertFalse((consumer / optional).exists())
            self.assertEqual([], self.verify(consumer, skills))

    def test_existing_project_preserves_guidance_and_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            consumer = temporary / "consumer"
            shutil.copytree(ROOT / "tests/fixtures/existing-project", consumer)
            original_agents = (consumer / "AGENTS.md").read_text()
            original_context = (consumer / "CONTEXT.md").read_bytes()
            self.configure(consumer)
            skills = self.install_skills(temporary / "vendor/location")
            self.assertTrue((consumer / "AGENTS.md").read_text().startswith(original_agents.rstrip()))
            self.assertEqual(original_context, (consumer / "CONTEXT.md").read_bytes())
            self.assertFalse((consumer / "docs/domain").exists())
            self.assertEqual([], self.verify(consumer, skills))

    def test_accepts_skill_directories_from_several_locations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            consumer = temporary / "consumer"
            consumer.mkdir()
            self.configure(consumer)
            skills = self.install_skills(temporary / "first/location")
            moved = skills.pop()
            other = temporary / "second/location" / moved.name
            other.parent.mkdir(parents=True)
            moved.rename(other)
            skills.append(other)
            self.assertEqual([], self.verify(consumer, skills))

    def test_rejects_missing_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            consumer = temporary / "consumer"
            consumer.mkdir()
            self.configure(consumer)
            skills = self.install_skills(temporary / "skills")
            skills = [path for path in skills if path.name != "clarify-intent"]
            errors = self.verify(consumer, skills)
            self.assertTrue(any("missing installed dependencies: clarify-intent" in error for error in errors))

    def test_rejects_mismatched_name_and_broken_reference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            consumer = temporary / "consumer"
            consumer.mkdir()
            self.configure(consumer)
            skills = self.install_skills(temporary / "skills")
            target = next(path for path in skills if path.name == "clarify-intent") / "SKILL.md"
            target.write_text(target.read_text().replace("name: clarify-intent", "name: wrong-name", 1) + "\n[Missing](references/nope.md)\n")
            errors = self.verify(consumer, skills)
            self.assertTrue(any("does not match directory" in error for error in errors))
            self.assertTrue(any("broken relative reference" in error for error in errors))

    def test_rejects_nested_configuration_and_escaping_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            consumer = temporary / "consumer"
            consumer.mkdir()
            self.configure(consumer)
            config = consumer / ".agents/workflows.yaml"
            config.write_text(config.read_text().replace("path: docs/domain", "path: ../domain"))
            nested = consumer / "package/.agents/workflows.yaml"
            nested.parent.mkdir(parents=True)
            nested.write_text(CONFIG)
            skills = self.install_skills(temporary / "skills")
            errors = self.verify(consumer, skills)
            self.assertTrue(any("nested workflow configuration" in error for error in errors))
            self.assertIn("artifacts.domain.path escapes the consumer root: ../domain", errors)

    def test_disabled_capability_needs_no_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            consumer = temporary / "consumer"
            consumer.mkdir()
            self.configure(consumer)
            skills = self.install_skills(temporary / "skills")
            self.assertFalse((consumer / "docs/meetings").exists())
            self.assertEqual([], self.verify(consumer, skills))

    def test_rejects_mutable_distribution_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            consumer = temporary / "consumer"
            consumer.mkdir()
            self.configure(consumer)
            config = consumer / ".agents/workflows.yaml"
            config.write_text(config.read_text().replace("e9d7dbb926931e2c7970e547fdb42b9906bb4cab", "latest"))
            skills = self.install_skills(temporary / "skills")
            errors = self.verify(consumer, skills)
            self.assertTrue(any("exact semantic release version" in error for error in errors))

    def test_surfaces_locally_modified_vendored_skill(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            consumer = temporary / "consumer"
            consumer.mkdir()
            self.configure(consumer)
            skills = self.install_skills(temporary / "skills")
            target = next(path for path in skills if path.name == "configure-project") / "SKILL.md"
            target.write_text(target.read_text() + "\nLocal change.\n")
            errors = self.verify(consumer, skills)
            self.assertIn("configure-project has locally modified file: SKILL.md", errors)


if __name__ == "__main__":
    unittest.main()
