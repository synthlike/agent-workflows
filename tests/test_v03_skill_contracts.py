from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


class V03SkillContractTests(unittest.TestCase):
    def skill(self, name: str) -> str:
        return (SKILLS / name / "SKILL.md").read_text()

    def test_technical_baseline_covers_common_contract(self) -> None:
        text = self.skill("establish-technical-baseline")
        for required in (
            "## Establish the boundary",
            "## Verify the stack",
            "## Assess applicable foundations",
            "## Choose a location",
            "## Confirm",
            "## Write and report",
            "Wait for explicit approval",
            "every changed file",
            "do not claim that a baseline is established",
        ):
            self.assertIn(required, text)

    def test_technical_baseline_preserves_authority(self) -> None:
        text = self.skill("establish-technical-baseline")
        for classification in (
            "Verified fact",
            "Approved convention",
            "Recommendation",
            "Accepted decision",
            "Open decision",
            "Deferred product question",
        ):
            self.assertIn(classification, text)
        self.assertIn("supporting index", text)
        self.assertIn("link the ARP instead of copying", text)

    def test_technical_baseline_handles_new_and_existing_projects(self) -> None:
        text = self.skill("establish-technical-baseline")
        self.assertIn("Prefer an existing project-approved", text)
        self.assertIn("If none exists, propose", text)
        self.assertIn("Preserve existing documentation and conventions", text)
        self.assertNotRegex(text, re.compile(r"docs/(?:architecture|engineering)/"))

    def test_technical_baseline_template_separates_decision_states(self) -> None:
        template = (
            SKILLS
            / "establish-technical-baseline"
            / "references/technical-baseline-template.md"
        ).read_text()
        for heading in (
            "## Fixed technology constraints",
            "## Compatibility and prerequisites",
            "## Approved conventions",
            "## Recommendations awaiting approval",
            "## Open decisions",
            "## Deferred product questions",
            "## Verification and operating commands",
            "## References",
        ):
            self.assertIn(heading, template)


if __name__ == "__main__":
    unittest.main()
