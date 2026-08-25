from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
RECORD_STORE = ROOT / "backends/record-store"
BUNDLED = ROOT / "skills/configure-workflows/references/backends/record-store"
SPECIFICATION = ROOT / "docs/specifications/strict-record-migration.md"


class MigrationContractTests(unittest.TestCase):
    def test_machine_schemas_are_versioned_strict_and_digest_bound(self) -> None:
        snapshot = json.loads((RECORD_STORE / "migration-snapshot.schema.json").read_text())
        plan = json.loads((RECORD_STORE / "migration-plan.schema.json").read_text())
        journal = json.loads((RECORD_STORE / "migration-journal.schema.json").read_text())
        for name, schema, version_field in (
            ("snapshot", snapshot, "snapshot_version"),
            ("plan", plan, "plan_version"),
            ("journal", journal, "journal_version"),
        ):
            with self.subTest(name=name):
                self.assertFalse(schema["additionalProperties"])
                self.assertEqual(1, schema["properties"][version_field]["const"])
                self.assertEqual("object", schema["type"])
        self.assertIn("content_sha256", snapshot["required"])
        self.assertIn("issue", snapshot["required"])
        self.assertEqual(
            {"kind", "status", "assignee", "labels", "comments", "relationships"},
            set(snapshot["$defs"]["issue"]["required"]),
        )
        self.assertIn("digest", plan["required"])
        self.assertIn("source_inventory_sha256", plan["properties"]["freeze"]["required"])
        self.assertEqual(3, plan["properties"]["stages"]["minItems"])
        self.assertEqual(3, plan["properties"]["stages"]["maxItems"])
        self.assertEqual(
            {"copy-verify", "route-cutover", "source-retirement"},
            set(
                plan["properties"]["stages"]["items"]["properties"]["name"]["enum"]
            ),
        )
        self.assertIn("journal_revision", journal["required"])
        self.assertEqual(
            {"copy-verify", "route-cutover", "source-retirement", "staged-cleanup"},
            set(journal["properties"]["approvals"]["required"]),
        )
        self.assertEqual(
            ["pre-cutover", "roll-forward"],
            journal["properties"]["recovery_direction"]["enum"],
        )

    def test_capability_schema_2_is_bundled_and_does_not_claim_implementation(self) -> None:
        expected_fields = {
            "backend_type", "issue_migration_operations", "issue_operations",
            "record_migration_operations", "record_operations", "record_types",
            "schema_version",
        }
        for backend_type in ("local-markdown", "github", "bear"):
            with self.subTest(backend_type=backend_type):
                source = RECORD_STORE / f"{backend_type}.capabilities.json"
                bundled = BUNDLED / source.name
                self.assertEqual(source.read_bytes(), bundled.read_bytes())
                declaration = json.loads(source.read_text())
                self.assertEqual(expected_fields, set(declaration))
                self.assertEqual(2, declaration["schema_version"])
                self.assertEqual([], declaration["record_migration_operations"])
                self.assertEqual([], declaration["issue_migration_operations"])

    def test_specification_records_fidelity_stages_matrix_and_exclusions(self) -> None:
        text = SPECIFICATION.read_text()
        required = (
            "exact title and content plus SHA-256",
            "active and retained historical records",
            "portable-represented",
            "provider-informational",
            "unsupported",
            "copy-verify",
            "route-cutover",
            "source-retirement",
            "staged-cleanup",
            "cooperative source-route write freeze",
            "recovery direction is `pre-cutover`",
            "changes irreversibly to `roll-forward`",
            "local Markdown | GitHub",
            "GitHub | Bear",
            "Bear never accepts `issues`",
            "Same-backend-type moves",
            "Free-form Markdown links remain byte-for-byte unchanged",
            "Project configuration cannot declare",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_existing_route_spec_disallows_only_implicit_migration(self) -> None:
        text = (
            ROOT / "docs/specifications/record-routing-and-backend-contracts.md"
        ).read_text()
        self.assertIn("### Explicit route migration", text)
        self.assertIn("MUST NOT move existing records implicitly", text)
        self.assertIn("strict-record-migration.md", text)
        self.assertIn("After verified cutover, recovery MUST roll forward", text)


if __name__ == "__main__":
    unittest.main()
