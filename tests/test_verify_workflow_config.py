from pathlib import Path
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verify_workflow_config import validate  # noqa: E402


class WorkflowConfigIdentityTests(unittest.TestCase):
    def validate_version(self, version: str, source: str = "github.com/acme/workflows") -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "workflows.yaml"
            path.write_text(
                "schema_version: 3\n"
                "distribution:\n"
                f"  source: {source}\n"
                f"  version: {version}\n"
            )
            return validate(path)

    def test_accepts_exact_release_versions(self) -> None:
        for version in ("0.1.0", "v0.1.0", "v1.2.3-rc.1", "1.2.3+build.7"):
            with self.subTest(version=version):
                self.assertEqual([], self.validate_version(version))

    def test_accepts_immutable_commit_shas(self) -> None:
        for version in ("a" * 40, "0123456789abcdef" * 4):
            with self.subTest(length=len(version)):
                self.assertEqual([], self.validate_version(version))

    def test_rejects_mutable_versions_and_branches(self) -> None:
        for version in ("latest", "unreleased", "main", "develop", "feature/install", "1.x"):
            with self.subTest(version=version):
                self.assertTrue(self.validate_version(version))

    def test_rejects_missing_distribution_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "workflows.yaml"
            path.write_text("schema_version: 3\ndistribution:\n")
            self.assertEqual(
                ["missing distribution.source", "missing distribution.version"],
                validate(path),
            )

    def test_rejects_schema_2_and_obsolete_top_level_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "workflows.yaml"
            path.write_text(
                "schema_version: 2\n"
                "distribution:\n"
                "  source: github.com/acme/workflows\n"
                "  version: v1.2.3\n"
                "issue_tracker:\n"
                "artifacts:\n"
                "specifications:\n"
            )
            self.assertEqual(
                [
                    "schema_version must be 3",
                    "obsolete schema field: issue_tracker",
                    "obsolete schema field: artifacts",
                    "obsolete schema field: specifications",
                ],
                validate(path),
            )

    def test_rejects_template_placeholders(self) -> None:
        errors = self.validate_version(
            "REQUIRED_EXACT_VERSION_OR_COMMIT_SHA",
            source="REQUIRED_DISTRIBUTION_SOURCE",
        )
        self.assertEqual(
            [
                "distribution.source is still a placeholder",
                "distribution.version is still a placeholder",
            ],
            errors,
        )


if __name__ == "__main__":
    unittest.main()
