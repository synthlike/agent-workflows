from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "skills/configure-project/references"
sys.path.insert(0, str(REFERENCES))
from consumer import parse_config  # noqa: E402


EXPECTED_CAPABILITIES = {
    "research": {"enabled": True, "path": "docs/research"},
    "questionnaires": {"enabled": True, "path": "docs/questionnaires"},
    "technical_baselines": {"enabled": True, "path": "docs/engineering"},
    "prototypes": {"enabled": False, "path": "docs/prototypes"},
    "handoffs": {"enabled": False, "path": ".agents/handoffs"},
}


class ArtifactRetentionTests(unittest.TestCase):
    def test_configuration_template_has_supporting_artifact_defaults(self) -> None:
        config = parse_config((REFERENCES / "workflow-config.example.yaml").read_text())
        artifacts = config["artifacts"]
        for name, expected in EXPECTED_CAPABILITIES.items():
            with self.subTest(capability=name):
                self.assertEqual(expected, artifacts[name])

    def test_affected_workflows_follow_repository_retention_policy(self) -> None:
        for name in (
            "research-question",
            "prepare-questionnaire",
            "establish-technical-baseline",
            "prototype-design",
            "prepare-handoff",
        ):
            text = (ROOT / "skills" / name / "SKILL.md").read_text()
            with self.subTest(skill=name):
                self.assertIn(".agents/workflows.yaml", text)
                self.assertIn("disabled", text)
                self.assertIn("without approval", text)

    def test_configuration_uses_project_context_not_rigid_profiles(self) -> None:
        text = (ROOT / "skills/configure-project/SKILL.md").read_text()
        self.assertIn("what kind of project this is", text)
        self.assertIn("how people and agents will collaborate", text)
        self.assertIn("recommend each capability individually", text)
        self.assertIn("Do not use rigid project-type profiles", text)
        self.assertIn("confirm one decision at a time", text)


if __name__ == "__main__":
    unittest.main()
