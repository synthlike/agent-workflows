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

    def test_regression_capture_requires_an_established_defect_and_approval(self) -> None:
        text = self.skill("capture-regression")
        for required in (
            "## Verify the starting point",
            "accepted and either reliably reproduced",
            "stop and use `investigate-failure`",
            "## Select the test seam",
            "## Confirm",
            "Wait for explicit approval before writing",
        ):
            self.assertIn(required, text)

    def test_regression_capture_proves_the_pre_fix_failure_without_production_changes(self) -> None:
        text = self.skill("capture-regression")
        for required in (
            "fails before the production fix",
            "Change only approved test and fixture files",
            "Do not change production code",
            "fails at the intended assertion or observable signal",
            "unrelated setup or environment errors do not explain it",
            "Do not commit automatically",
        ):
            self.assertIn(required, text)

    def test_regression_capture_handles_impractical_automation_and_red_policy(self) -> None:
        text = self.skill("capture-regression")
        self.assertIn("If durable automation is impractical", text)
        self.assertIn("policy prohibits a failing commit", text)
        self.assertIn("land atomically", text)

    def test_issue_triage_checks_duplicates_and_separates_claims_from_evidence(self) -> None:
        text = self.skill("triage-issue")
        for required in (
            "## Load the project contract",
            "## Check prior work",
            "exact or functional duplicates",
            "Reported impact",
            "Verified evidence",
            "Do not invent urgency, severity",
        ):
            self.assertIn(required, text)

    def test_issue_triage_routes_uncertainty_and_requires_approval(self) -> None:
        text = self.skill("triage-issue")
        for route in (
            "`investigate-failure`",
            "`research-question`",
            "`clarify-intent`",
            "`develop-rfc`",
            "`plan-implementation`",
        ):
            self.assertIn(route, text)
        self.assertIn("Before any issue creation or material rewrite", text)
        self.assertIn("Wait for approval", text)
        self.assertIn("Perform only the approved operations", text)

    def test_issue_triage_template_supports_non_issue_dispositions(self) -> None:
        template = (
            SKILLS / "triage-issue" / "references/triage-proposal-template.md"
        ).read_text()
        for required in (
            "## Existing and authoritative context",
            "## Evidence and missing information",
            "## Recommended disposition",
            "duplicate or covered",
            "route to another workflow",
            "## Proposed backend operations",
        ):
            self.assertIn(required, template)


if __name__ == "__main__":
    unittest.main()
