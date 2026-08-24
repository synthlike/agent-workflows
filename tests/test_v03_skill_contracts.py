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

    def test_failure_investigation_is_diagnostic_and_hypothesis_driven(self) -> None:
        text = self.skill("investigate-failure")
        for required in (
            "## Bound the investigation",
            "## Reproduce",
            "## Test hypotheses",
            "## Control probes",
            "## Conclude",
            "## Confirm publication",
            "supported, weakened, falsified, or untested",
            "bounded uncertainty",
            "do not create a permanent test or implement a production fix",
        ):
            self.assertIn(required, text)

    def test_failure_investigation_controls_probes_and_issue_writes(self) -> None:
        text = self.skill("investigate-failure")
        self.assertIn("Track every probe", text)
        self.assertIn("Remove it before completion", text)
        self.assertIn("Present the findings before writing", text)
        self.assertIn("Do not create follow-up work, change issue status", text)

    def test_failure_findings_template_supports_reproduced_and_uncertain_results(self) -> None:
        template = (
            SKILLS
            / "investigate-failure"
            / "references/failure-findings-template.md"
        ).read_text()
        for required in (
            "## Expected and observed behavior",
            "## Environment and reproduction",
            "## Evidence",
            "## Hypotheses",
            "a supported root cause",
            "bounded uncertainty",
            "## Probes and repository state",
            "## Recommended next action",
        ):
            self.assertIn(required, template)


if __name__ == "__main__":
    unittest.main()
