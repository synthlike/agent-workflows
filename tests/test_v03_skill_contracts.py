from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

SKILL_EXPECTATIONS = {
    "establish-technical-baseline": (
        "## Establish the boundary", "## Verify the stack", "## Assess applicable foundations",
        "## Choose a location", "## Confirm", "## Write and report", "Wait for explicit approval",
        "every changed file", "do not claim that a baseline is established", "Verified fact",
        "Approved convention", "Recommendation", "Accepted decision", "Open decision",
        "Deferred product question", "supporting index", "link the ARP instead of copying",
        "Prefer an existing project-approved", "configured technical-baseline path",
        "Preserve existing documentation and conventions",
    ),
    "investigate-failure": (
        "## Bound the investigation", "## Reproduce", "## Test hypotheses", "## Control probes",
        "## Conclude", "## Confirm publication", "supported, weakened, falsified, or untested",
        "bounded uncertainty", "do not create a permanent test or implement a production fix",
        "Track every probe", "Remove it before completion", "Present the findings before writing",
        "Do not create follow-up work, change issue status",
    ),
    "capture-regression": (
        "## Verify the starting point", "accepted and either reliably reproduced",
        "stop and use `investigate-failure`", "## Select the test seam", "## Confirm",
        "Wait for explicit approval before writing", "fails before the production fix",
        "Change only approved test and fixture files", "Do not change production code",
        "fails at the intended assertion or observable signal",
        "unrelated setup or environment errors do not explain it", "Do not commit automatically",
        "If durable automation is impractical", "policy prohibits a failing commit", "land atomically",
    ),
    "triage-issue": (
        "## Load the project contract", "## Check prior work", "exact or functional duplicates",
        "Reported impact", "Verified evidence", "Do not invent urgency, severity",
        "`investigate-failure`", "`research-question`", "`clarify-intent`", "`develop-rfc`",
        "`plan-implementation`", "Before any issue creation or material rewrite", "Wait for approval",
        "Perform only the approved operations",
    ),
    "review-implementation": (
        "## Establish scope", "specifications define agreed behavior", "accepted ARPs constrain",
        "issues define the executable slice", "actual code and configuration",
        "A passing test suite is evidence, not proof", "Do not edit code, configuration, tests",
        "Return exactly one verdict", "Conforms:", "Conforms with follow-up:", "Does not conform:",
        "Present the complete review and verdict before any issue operation",
    ),
    "close-initiative": (
        "## Load the initiative", "Do not assume that issue status proves delivery",
        "## Verify outcomes", "Reconcile every unresolved, blocked, cancelled, and deferred item",
        "Do not present cancelled, deferred, or merely planned scope as delivered", "**Achieved:**",
        "**Partially achieved:**", "**Abandoned:**", "Wait for explicit approval",
        "Do not create a separate canonical closure-report type", "do not close the initiative",
    ),
    "frame-product-problem": (
        "Ask exactly one question at a time", "the proposed solution",
        "current behavior, alternatives, and workarounds", "Founder belief", "Direct observation",
        "External evidence", "Interpretation", "Unknown", "counter-hypotheses",
        "Prefer an existing project-approved", "Never assume a fixed consumer path",
        "Wait for explicit approval before writing", "supporting evidence",
        "ask about concrete past behavior", "avoid pitching the solution",
        "avoid hypothetical compliments", "respect consent, privacy, confidentiality",
        "Do not fabricate participants", "cannot substitute for customer or behavioral evidence",
        "`Unexamined`", "`Supported`", "`Weakened`", "`Contradicted`", "`Inconclusive`",
        "continue, narrow, reframe, pivot, or stop", "The founder decides",
        "Never label the product idea or problem “validated”",
    ),
}

REFERENCE_EXPECTATIONS = {
    "establish-technical-baseline/references/technical-baseline-template.md": (
        "## Fixed technology constraints", "## Compatibility and prerequisites",
        "## Approved conventions", "## Recommendations awaiting approval", "## Open decisions",
        "## Deferred product questions", "## Verification and operating commands", "## References",
    ),
    "investigate-failure/references/failure-findings-template.md": (
        "## Expected and observed behavior", "## Environment and reproduction", "## Evidence",
        "## Hypotheses", "a supported root cause", "bounded uncertainty",
        "## Probes and repository state", "## Recommended next action",
    ),
    "triage-issue/references/triage-proposal-template.md": (
        "## Existing and authoritative context", "## Evidence and missing information",
        "## Recommended disposition", "duplicate or covered", "route to another workflow",
        "## Proposed backend operations",
    ),
    "review-implementation/references/implementation-review-template.md": (
        "## Authoritative intent", "## Implementation evidence", "## Verification performed",
        "**Expectation:**", "**Evidence:**", "**Impact:**", "**Recommended disposition:**",
        "## Limitations and confidence",
    ),
    "close-initiative/references/initiative-closure-template.md": (
        "## Outcome evidence", "## Delivered value", "## Gaps and limitations",
        "## Work reconciliation", "## Proposed follow-up work", "## Lessons and authority routing",
        "## Proposed artifact operations",
    ),
    "frame-product-problem/references/problem-framing-template.md": (
        "## Proposed solution", "## Problem hypothesis", "## Actors and audience segments",
        "## Current behavior, alternatives, and workarounds", "## Claims and evidence",
        "## Counter-hypotheses", "## Risky assumptions and validation plan",
        "## Evidence log and reassessment", "## Current recommendation",
    ),
}


class V03SkillContractTests(unittest.TestCase):
    def test_skill_contracts(self) -> None:
        for name, expected in SKILL_EXPECTATIONS.items():
            text = (SKILLS / name / "SKILL.md").read_text()
            for value in expected:
                with self.subTest(skill=name, value=value):
                    self.assertIn(value, text)

    def test_reference_contracts(self) -> None:
        for relative, expected in REFERENCE_EXPECTATIONS.items():
            text = (SKILLS / relative).read_text()
            for value in expected:
                with self.subTest(reference=relative, value=value):
                    self.assertIn(value, text)

    def test_project_owned_locations_are_not_hardcoded(self) -> None:
        baseline = (SKILLS / "establish-technical-baseline/SKILL.md").read_text()
        product = (SKILLS / "frame-product-problem/SKILL.md").read_text()
        self.assertNotRegex(baseline, re.compile(r"docs/(?:architecture|engineering)/"))
        self.assertNotIn("docs/product/", product)


if __name__ == "__main__":
    unittest.main()
