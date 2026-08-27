from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import importlib.util
import json
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backends/record-store"
sys.path.insert(0, str(BACKEND))
from contract import (  # noqa: E402
    IssueRequest,
    MigrationRequest,
    RecordError,
    RecordRequest,
    migration_reference_key,
)

SPEC = importlib.util.spec_from_file_location(
    "local_markdown_migration_adapter", BACKEND / "local-markdown.py"
)
assert SPEC and SPEC.loader
local_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = local_module
SPEC.loader.exec_module(local_module)
LocalMarkdownAdapter = local_module.LocalMarkdownAdapter
from tests.migration_adapter_contract import MigrationAdapterContract  # noqa: E402


class LocalMigrationAdapterTests(MigrationAdapterContract, unittest.TestCase):
    record_type = "research"
    record_destination = {"path": "docs/research"}
    issue_destination = {"root": ".project"}

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        base = Path(self.temporary.name)
        source_counter = iter(range(1, 100))
        destination_counter = iter(range(1, 100))
        self.source = LocalMarkdownAdapter(
            base / "source",
            "source",
            clock=lambda: f"2026-08-25T00:00:{next(source_counter):02d}Z",
        )
        self.destination = LocalMarkdownAdapter(
            base / "destination",
            "destination",
            clock=lambda: f"2026-08-26T00:00:{next(destination_counter):02d}Z",
        )

    def tearDown(self):
        self.temporary.cleanup()

    def migration_request(
        self,
        adapter,
        operation,
        record_type,
        destination,
        *,
        snapshot=None,
        destination_reference=None,
        reference_map=None,
    ):
        return MigrationRequest(
            operation=operation,
            backend=adapter.backend,
            backend_type="local-markdown",
            record_type=record_type,
            destination=destination,
            snapshot=snapshot,
            destination_reference=destination_reference,
            reference_map=reference_map or {},
        )

    def create_record(self, adapter, *, title="Finding", content="Exact bytes\nwith [[links]].\n"):
        return adapter.execute(
            RecordRequest(
                operation="create",
                backend=adapter.backend,
                record_type=self.record_type,
                destination=self.record_destination,
                title=title,
                content=content,
            )
        ).record

    def export_records(self, adapter):
        return adapter.execute_migration(
            self.migration_request(
                adapter,
                "export-history",
                self.record_type,
                self.record_destination,
            )
        ).snapshots

    def test_migration_commands_expose_snapshot_import_and_verification(self):
        self.create_record(self.source)
        output = StringIO()
        with redirect_stdout(output):
            result = local_module.main(
                [
                    "--root", str(self.source.root), "--backend", "source",
                    "--destination", "docs/research", "migration-export",
                    "--record-type", self.record_type,
                ]
            )
        self.assertEqual(0, result)
        snapshot = json.loads(output.getvalue())["snapshots"][0]
        snapshot_file = self.source.root / "snapshot.json"
        snapshot_file.write_text(json.dumps(snapshot))

        output = StringIO()
        with redirect_stdout(output):
            result = local_module.main(
                [
                    "--root", str(self.destination.root), "--backend", "destination",
                    "--destination", "docs/research", "migration-import",
                    "--record-type", self.record_type, "--snapshot-file", str(snapshot_file),
                ]
            )
        self.assertEqual(0, result)
        imported = json.loads(output.getvalue())
        self.assertTrue(imported["verified"])
        self.assertEqual(snapshot["content"], imported["snapshot"]["content"])

    def test_non_issue_import_verify_replay_and_retirement_are_lossless(self):
        source = self.create_record(self.source)
        snapshot = self.export_records(self.source)[0]

        imported = self.destination.execute_migration(
            self.migration_request(
                self.destination,
                "import",
                self.record_type,
                self.record_destination,
                snapshot=snapshot,
            )
        )
        self.assertEqual(source.id, imported.snapshot["identity"]["semantic_id"])
        self.assertEqual("Exact bytes\nwith [[links]].\n", imported.snapshot["content"])
        self.assertTrue(imported.verified)

        verified = self.destination.execute_migration(
            self.migration_request(
                self.destination,
                "verify",
                self.record_type,
                self.record_destination,
                snapshot=snapshot,
                destination_reference=imported.reference,
            )
        )
        replay = self.destination.execute_migration(
            self.migration_request(
                self.destination,
                "import",
                self.record_type,
                self.record_destination,
                snapshot=snapshot,
            )
        )
        self.assertEqual(verified.revision, replay.revision)

        retired = self.source.execute_migration(
            self.migration_request(
                self.source,
                "retire",
                self.record_type,
                self.record_destination,
                snapshot=snapshot,
                destination_reference=imported.reference,
            )
        )
        self.assertTrue(retired.snapshot["lifecycle"]["archived"])
        self.assertEqual(snapshot["content"], retired.snapshot["content"])
        replay_retirement = self.source.execute_migration(
            self.migration_request(
                self.source,
                "retire",
                self.record_type,
                self.record_destination,
                snapshot=snapshot,
                destination_reference=imported.reference,
            )
        )
        self.assertEqual(retired.revision, replay_retirement.revision)

    def test_non_issue_collision_and_stale_retirement_write_nothing(self):
        source = self.create_record(self.source)
        snapshot = self.export_records(self.source)[0]
        self.create_record(self.destination, content="occupied")
        before = tuple((self.destination.root / "docs/research").glob("*.md"))
        with self.assertRaises(RecordError) as raised:
            self.destination.execute_migration(
                self.migration_request(
                    self.destination,
                    "import",
                    self.record_type,
                    self.record_destination,
                    snapshot=snapshot,
                )
            )
        self.assertEqual("duplicate_id", raised.exception.code)
        self.assertEqual(before, tuple((self.destination.root / "docs/research").glob("*.md")))

        changed = self.source.execute(
            RecordRequest(
                operation="update",
                backend="source",
                record_type=self.record_type,
                destination=self.record_destination,
                id=source.id,
                expected_revision=source.revision,
                content="changed",
            )
        ).record
        with self.assertRaises(RecordError) as stale:
            self.source.execute_migration(
                self.migration_request(
                    self.source,
                    "retire",
                    self.record_type,
                    self.record_destination,
                    snapshot=snapshot,
                    destination_reference=changed.reference,
                )
            )
        self.assertEqual("stale_revision", stale.exception.code)
        self.assertFalse(
            self.source.execute(
                RecordRequest(
                    operation="read",
                    backend="source",
                    record_type=self.record_type,
                    destination=self.record_destination,
                    id=source.id,
                )
            ).record.metadata["archived"]
        )

    def issue(self, adapter, operation, **values):
        return adapter.execute_issue(
            IssueRequest(
                operation=operation,
                backend=adapter.backend,
                destination=self.issue_destination,
                **values,
            )
        ).issue

    def export_issues(self, adapter):
        return adapter.execute_migration(
            self.migration_request(
                adapter,
                "export-history",
                "issues",
                self.issue_destination,
            )
        ).snapshots

    def test_issue_import_preserves_state_comments_relationships_and_exact_body(self):
        blocker = self.issue(
            self.source, "create", title="Blocker", body="blocker", kind="task"
        )
        parent = self.issue(
            self.source, "create", title="Parent", body="parent", kind="initiative"
        )
        child = self.issue(
            self.source,
            "create",
            title="Child",
            body="body with https://example.invalid/raw",
            kind="task",
            labels=("migration", "priority"),
        )
        child = self.issue(
            self.source,
            "parent",
            id=child.id,
            expected_revision=child.revision,
            parent_id=parent.id,
        )
        child = self.issue(
            self.source,
            "block",
            id=child.id,
            expected_revision=child.revision,
            blocker_id=blocker.id,
        )
        child = self.issue(
            self.source,
            "claim",
            id=child.id,
            expected_revision=child.revision,
            assignee="sam",
        )
        child = self.issue(
            self.source,
            "comment",
            id=child.id,
            expected_revision=child.revision,
            assignee="alex",
            body="Do not rewrite [[opaque-link]].",
        )
        snapshots = {item["identity"]["semantic_id"]: item for item in self.export_issues(self.source)}

        imported = {}
        mapping = {}
        for source_issue in (blocker, parent):
            snapshot = snapshots[source_issue.id]
            response = self.destination.execute_migration(
                self.migration_request(
                    self.destination,
                    "import",
                    "issues",
                    self.issue_destination,
                    snapshot=snapshot,
                )
            )
            imported[source_issue.id] = response
            mapping[migration_reference_key(snapshot["source"]["reference"])] = response.reference

        child_snapshot = snapshots[child.id]
        child_import = self.destination.execute_migration(
            self.migration_request(
                self.destination,
                "import",
                "issues",
                self.issue_destination,
                snapshot=child_snapshot,
                reference_map=mapping,
            )
        )
        self.assertEqual(child_snapshot["content"], child_import.snapshot["content"])
        self.assertEqual("claimed", child_import.snapshot["issue"]["status"])
        self.assertEqual("sam", child_import.snapshot["issue"]["assignee"])
        self.assertEqual(["migration", "priority"], child_import.snapshot["issue"]["labels"])
        self.assertEqual(2, len(child_import.snapshot["issue"]["relationships"]))
        self.assertEqual(1, len(child_import.snapshot["issue"]["comments"]))

        replay = self.destination.execute_migration(
            self.migration_request(
                self.destination,
                "import",
                "issues",
                self.issue_destination,
                snapshot=child_snapshot,
                reference_map=mapping,
            )
        )
        self.assertEqual(child_import.revision, replay.revision)

        retired = self.source.execute_migration(
            self.migration_request(
                self.source,
                "retire",
                "issues",
                self.issue_destination,
                snapshot=child_snapshot,
                destination_reference=child_import.reference,
            )
        )
        self.assertEqual("cancelled", retired.snapshot["issue"]["status"])
        self.assertIn("Destination is authoritative", retired.snapshot["content"])

    def test_issue_collision_and_stale_retirement_do_not_mutate(self):
        issue = self.issue(self.source, "create", title="Source", body="body", kind="task")
        snapshot = self.export_issues(self.source)[0]
        occupied = self.issue(
            self.destination, "create", title="Occupied", body="occupied", kind="task"
        )
        with self.assertRaises(RecordError) as collision:
            self.destination.execute_migration(
                self.migration_request(
                    self.destination,
                    "import",
                    "issues",
                    self.issue_destination,
                    snapshot=snapshot,
                )
            )
        self.assertEqual("duplicate_id", collision.exception.code)
        self.assertEqual(1, len(self.export_issues(self.destination)))

        changed = self.issue(
            self.source,
            "comment",
            id=issue.id,
            expected_revision=issue.revision,
            assignee="writer",
            body="concurrent change",
        )
        with self.assertRaises(RecordError) as stale:
            self.source.execute_migration(
                self.migration_request(
                    self.source,
                    "retire",
                    "issues",
                    self.issue_destination,
                    snapshot=snapshot,
                    destination_reference=occupied.reference,
                )
            )
        self.assertEqual("stale_revision", stale.exception.code)
        current = self.issue(self.source, "read", id=issue.id)
        self.assertEqual(changed.revision, current.revision)
        self.assertEqual("open", current.status)
        self.assertNotIn("Destination is authoritative", current.body)

    def test_terminal_issue_retirement_adds_provenance_without_reopening(self):
        issue = self.issue(self.source, "create", title="Done", body="body", kind="task")
        issue = self.issue(
            self.source,
            "resolve",
            id=issue.id,
            expected_revision=issue.revision,
            body="accepted",
        )
        snapshot = self.export_issues(self.source)[0]
        imported = self.destination.execute_migration(
            self.migration_request(
                self.destination,
                "import",
                "issues",
                self.issue_destination,
                snapshot=snapshot,
            )
        )
        retired = self.source.execute_migration(
            self.migration_request(
                self.source,
                "retire",
                "issues",
                self.issue_destination,
                snapshot=snapshot,
                destination_reference=imported.reference,
            )
        )
        self.assertEqual("resolved", retired.snapshot["issue"]["status"])
        self.assertIn("Destination is authoritative", retired.snapshot["content"])
        replay = self.source.execute_migration(
            self.migration_request(
                self.source,
                "retire",
                "issues",
                self.issue_destination,
                snapshot=snapshot,
                destination_reference=imported.reference,
            )
        )
        self.assertEqual(retired.revision, replay.revision)

    def test_issue_import_rejects_unrepresentable_content_before_writing(self):
        issue = self.issue(self.source, "create", title="Issue", body="body", kind="task")
        snapshot = dict(self.export_issues(self.source)[0])
        snapshot["content"] = "provider body without local structure"
        snapshot["content_sha256"] = self.destination._sha256(snapshot["content"].encode())
        with self.assertRaises(RecordError) as raised:
            self.destination.execute_migration(
                self.migration_request(
                    self.destination,
                    "import",
                    "issues",
                    self.issue_destination,
                    snapshot=snapshot,
                )
            )
        self.assertEqual("invalid_state", raised.exception.code)
        self.assertFalse((self.destination.root / ".project/issues").exists())
        self.assertIsNotNone(issue)


if __name__ == "__main__":
    unittest.main()
