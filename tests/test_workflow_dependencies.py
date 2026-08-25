from pathlib import Path
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verify_workflow_dependencies import closure, validate  # noqa: E402


class WorkflowDependencyTests(unittest.TestCase):
    def fixture(
        self,
        alpha_body: str = "No cross-workflow routing.",
        rows: tuple[str, ...] = (
            "| `alpha-skill` | None |",
            "| `beta-skill` | None |",
            "| `configure-workflows` | None |",
        ),
    ) -> tuple[tempfile.TemporaryDirectory[str], Path, Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        for name, body in (
            ("alpha-skill", alpha_body),
            ("beta-skill", "No cross-workflow routing."),
            ("configure-workflows", "Configure the consumer."),
        ):
            directory = root / "skills" / name
            directory.mkdir(parents=True)
            (directory / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: Test skill.\n---\n\n# Test\n\n{body}\n"
            )
        table = root / "dependencies.md"
        table.write_text(
            "| Skill | Additional direct skill dependencies |\n"
            "| --- | --- |\n"
            + "\n".join(rows)
            + "\n"
        )
        return temporary, root, table

    def test_current_distribution_matches_published_table(self) -> None:
        root = Path(__file__).resolve().parents[1]
        _, errors = validate(root, root / "docs/workflow-dependencies.md")
        self.assertEqual([], errors)

    def test_rejects_unknown_dependency(self) -> None:
        temporary, root, table = self.fixture(
            rows=(
                "| `alpha-skill` | `missing-skill` |",
                "| `beta-skill` | None |",
                "| `configure-workflows` | None |",
            )
        )
        with temporary:
            _, errors = validate(root, table)
            self.assertIn("alpha-skill depends on unknown skill missing-skill", errors)

    def test_rejects_missing_skill_row(self) -> None:
        temporary, root, table = self.fixture(
            rows=(
                "| `alpha-skill` | None |",
                "| `configure-workflows` | None |",
            )
        )
        with temporary:
            _, errors = validate(root, table)
            self.assertIn("dependency table is missing skill beta-skill", errors)

    def test_rejects_missing_explicit_cross_skill_route(self) -> None:
        temporary, root, table = self.fixture("Route this work to `beta-skill`.")
        with temporary:
            _, errors = validate(root, table)
            self.assertIn("alpha-skill is missing declared dependencies: beta-skill", errors)

    def test_ignores_documentation_only_artifact_references(self) -> None:
        temporary, root, table = self.fixture(
            "Link the RFC, ARP, specification, issue, research, and prototype."
        )
        with temporary:
            _, errors = validate(root, table)
            self.assertEqual([], errors)

    def test_calculates_dependency_closure_with_cycles(self) -> None:
        dependencies = {
            "configure-workflows": set(),
            "alpha-skill": {"beta-skill"},
            "beta-skill": {"alpha-skill"},
        }
        self.assertEqual(
            {"configure-workflows", "alpha-skill", "beta-skill"},
            closure({"alpha-skill"}, dependencies),
        )


if __name__ == "__main__":
    unittest.main()
