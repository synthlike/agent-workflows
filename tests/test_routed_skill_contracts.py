from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

ROUTES = {
    "author-specification": "specs",
    "capture-meeting": "meetings",
    "capture-regression": "issues",
    "clarify-intent": None,
    "close-initiative": "issues",
    "develop-rfc": "rfcs",
    "establish-technical-baseline": "technical_baselines",
    "frame-product-problem": "problem_framing",
    "investigate-failure": "issues",
    "model-domain": "domain",
    "plan-implementation": "issues",
    "plan-initiative": "issues",
    "prepare-handoff": "handoffs",
    "prepare-questionnaire": "questionnaires",
    "prototype-design": "prototypes",
    "record-arp": "arps",
    "research-question": "research",
    "review-implementation": "issues",
    "triage-issue": "issues",
}


class RoutedSkillContractTests(unittest.TestCase):
    def test_every_existing_workflow_resolves_semantic_record_guidance(self) -> None:
        actual = {
            path.parent.name
            for path in SKILLS.glob("*/SKILL.md")
            if path.parent.name != "configure-workflows"
        }
        self.assertEqual(set(ROUTES), actual)
        for name, route in ROUTES.items():
            text = (SKILLS / name / "SKILL.md").read_text()
            with self.subTest(skill=name):
                self.assertIn(".agents/workflows.yaml", text)
                self.assertIn("docs/agents/records.md", text)
                self.assertIn("adapter", text.lower())
                self.assertRegex(text, r"route is (?:disabled|enabled)")
                self.assertRegex(text.lower(), r"do not construct|rather than constructing|or constructing")
                if route is not None:
                    self.assertIn(f"`{route}` route", text)

    def test_workflows_do_not_select_provider_storage_details(self) -> None:
        forbidden = (
            re.compile(r"docs/agents/issue-tracker\.md"),
            re.compile(r"configured [a-z-]+ path", re.I),
            re.compile(r"configured issue backend", re.I),
            re.compile(r"allocate the next", re.I),
            re.compile(r"docs/(?:domain|decisions|rfcs|specs|meetings|research|questionnaires|engineering|product|prototypes)"),
            re.compile(r"workflow:(?:record|issue):"),
        )
        for path in sorted(SKILLS.glob("*/SKILL.md")):
            if path.parent.name == "configure-workflows":
                continue
            text = path.read_text()
            for pattern in forbidden:
                with self.subTest(skill=path.parent.name, pattern=pattern.pattern):
                    self.assertNotRegex(text, pattern)

    def test_issue_owned_outputs_keep_their_authority_boundaries(self) -> None:
        initiative = (SKILLS / "plan-initiative/SKILL.md").read_text()
        investigation = (SKILLS / "investigate-failure/SKILL.md").read_text()
        regression = (SKILLS / "capture-regression/SKILL.md").read_text()
        review = (SKILLS / "review-implementation/SKILL.md").read_text()
        closure = (SKILLS / "close-initiative/SKILL.md").read_text()
        prototype = (SKILLS / "prototype-design/SKILL.md").read_text()

        self.assertIn("Initiative maps and decision tickets remain issue structures", initiative)
        self.assertIn("Do not create a separate failure-findings record", investigation)
        self.assertIn("do not create a separate regression record", regression)
        self.assertIn("do not create a separate review record", review)
        self.assertIn("Do not create a separate canonical closure-report type", closure)
        self.assertIn("durable prototype metadata and conclusions", prototype)
        self.assertIn("Executable prototype files may remain temporary or external", prototype)


if __name__ == "__main__":
    unittest.main()
