from __future__ import annotations

import hashlib

from contract import MigrationRequest, RecordError, RecordRequest


class MigrationAdapterContract:
    """Provider-independent migration checks reusable by every complete adapter."""

    source: object
    destination: object
    record_type: str
    record_destination: dict

    def create_record(self, adapter, *, title="Finding", content="Exact bytes\n"):
        raise NotImplementedError

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
            backend_type=adapter.backend_type,
            record_type=record_type,
            destination=destination,
            snapshot=snapshot,
            destination_reference=destination_reference,
            reference_map=reference_map or {},
        )

    def export_records(self, adapter):
        return adapter.execute_migration(
            self.migration_request(
                adapter,
                "export-history",
                self.record_type,
                self.record_destination,
            )
        ).snapshots

    def test_migration_contract_non_issue_copy_verify_replay_and_retirement(self):
        content = "Exact bytes\nwith an opaque [[reference]].\n"
        source = self.create_record(self.source, title="Portable", content=content)
        snapshots = self.export_records(self.source)
        self.assertEqual(1, len(snapshots))
        snapshot = snapshots[0]
        self.assertEqual(source.revision, snapshot["source"]["revision"])
        self.assertEqual(content, snapshot["content"])
        self.assertEqual(
            "sha256:" + hashlib.sha256(content.encode()).hexdigest(),
            snapshot["content_sha256"],
        )

        imported = self.destination.execute_migration(
            self.migration_request(
                self.destination,
                "import",
                self.record_type,
                self.record_destination,
                snapshot=snapshot,
            )
        )
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
        self.assertTrue(verified.verified)
        self.assertEqual(imported.revision, replay.revision)
        self.assertEqual(content, verified.snapshot["content"])

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
        self.assertEqual(content, retired.snapshot["content"])
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

    def test_migration_contract_exports_retained_history_and_rejects_stale_source(self):
        archived = self.create_record(self.source, title="Historical", content="retained")
        archived = self.source.execute(
            RecordRequest(
                operation="archive",
                backend=self.source.backend,
                record_type=self.record_type,
                destination=self.record_destination,
                id=archived.id,
                expected_revision=archived.revision,
            )
        ).record
        snapshots = self.export_records(self.source)
        historical = next(
            value for value in snapshots if value["identity"]["semantic_id"] == archived.id
        )
        self.assertTrue(historical["lifecycle"]["archived"])

        active = self.create_record(self.source, title="Mutable", content="before")
        snapshot = next(
            value
            for value in self.export_records(self.source)
            if value["identity"]["semantic_id"] == active.id
        )
        changed = self.source.execute(
            RecordRequest(
                operation="update",
                backend=self.source.backend,
                record_type=self.record_type,
                destination=self.record_destination,
                id=active.id,
                expected_revision=active.revision,
                content="after",
            )
        ).record
        with self.assertRaises(RecordError) as raised:
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
        self.assertEqual("stale_revision", raised.exception.code)
