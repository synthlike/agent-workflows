from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "skills/configure-workflows/references"
sys.path.insert(0, str(REFERENCES))
from consumer import parse_config  # noqa: E402


EXPECTED_CAPABILITIES = {
    "research": {"enabled": True, "backend": "local", "destination": {"path": "docs/research"}},
    "questionnaires": {"enabled": True, "backend": "local", "destination": {"path": "docs/questionnaires"}},
    "technical_baselines": {"enabled": True, "backend": "local", "destination": {"path": "docs/engineering"}},
    "problem_framing": {"enabled": True, "backend": "local", "destination": {"path": "docs/product"}},
    "prototypes": {"enabled": False, "backend": "local", "destination": {"path": "docs/prototypes"}},
    "handoffs": {"enabled": False, "backend": "local", "destination": {"path": ".agents/handoffs"}},
}


class ArtifactRetentionTests(unittest.TestCase):
    def test_configuration_template_has_supporting_artifact_defaults(self) -> None:
        config = parse_config((REFERENCES / "workflow-config.example.yaml").read_text())
        records = config["records"]
        for name, expected in EXPECTED_CAPABILITIES.items():
            with self.subTest(capability=name):
                self.assertEqual(expected, records[name])

    def test_configuration_does_not_require_git(self) -> None:
        text = (ROOT / "skills/configure-workflows/SKILL.md").read_text()
        self.assertIn("Git is not required", text)
        self.assertIn("whether the workspace is intentionally unversioned", text)
        self.assertIn("never initialize, change, or configure version control without approval", text)
        self.assertIn("preserve its conventions", text)

    def test_github_routes_require_preflight_and_reviewed_provisioning(self) -> None:
        text = (ROOT / "skills/configure-workflows/SKILL.md").read_text()
        self.assertIn("before recommending or asking approval for any route", text)
        self.assertIn("actual API identity", text)
        self.assertIn("complete record contract", text)
        self.assertIn("complete issue contract", text)
        self.assertIn("label-plan schema 2", text)
        self.assertIn("apply only the exact reviewed plan after approval", text)
        self.assertIn("exactly the guidance/helper pair for each backend type used", text)

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
        text = (ROOT / "skills/configure-workflows/SKILL.md").read_text()
        self.assertIn("what kind of project this is", text)
        self.assertIn("how people and agents will collaborate", text)
        self.assertIn("recommend each capability individually", text)
        self.assertIn("Profile questions may offer all-local, all-GitHub, or mixed", text)
        self.assertIn("expand every answer into explicit routes", text)
        self.assertIn("complete destination for every route", text)


if __name__ == "__main__":
    unittest.main()
