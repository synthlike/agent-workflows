"""Reusable behavior checks for semantic record adapters."""

from __future__ import annotations

from contract import RecordError, RecordReference, RecordRequest


class RecordAdapterContract:
    """Mixin. Subclasses provide adapter, backend, record_type, and destination."""

    adapter = None
    backend = ""
    record_type = ""
    destination = {}

    def request(self, operation: str, **values):
        return RecordRequest(
            operation=operation,
            backend=self.backend,
            record_type=self.record_type,
            destination=self.destination,
            **values,
        )

    def create(self, title="Compatibility notes", content="Initial findings", **values):
        response = self.adapter.execute(
            self.request("create", title=title, content=content, **values)
        )
        self.assertIsNotNone(response.record)
        return response.record

    def test_contract_create_read_and_structured_reference(self):
        created = self.create()
        read = self.adapter.execute(self.request("read", id=created.id)).record
        self.assertEqual(created.as_dict(), read.as_dict())
        self.assertEqual(self.backend, created.reference.backend)
        self.assertTrue(created.reference.id)
        self.assertEqual(created.title, created.reference.title)
        self.assertTrue(created.reference.href)
        self.assertTrue(created.revision.startswith("sha256:"))

    def test_contract_renders_opaque_cross_backend_references(self):
        rendered = self.adapter.render_reference(
            RecordReference(
                backend="other-instance",
                id="provider-native-id",
                title="Related [record]",
                href="https://example.test/records/42",
            )
        )
        self.assertEqual(
            "[Related \\[record\\]](<https://example.test/records/42>)",
            rendered,
        )
        self.assertEqual(
            "Unlinked record",
            self.adapter.render_reference(
                RecordReference.from_dict(
                    {"backend": "other-instance", "id": "native", "title": "Unlinked record"}
                )
            ),
        )

    def test_contract_list_and_search(self):
        first = self.create(title="Runtime compatibility", content="Supported versions")
        self.create(title="Customer interviews", content="Observed behavior")
        listed = self.adapter.execute(self.request("list")).records
        self.assertEqual(
            sorted([first.id, "customer-interviews"]),
            [record.id for record in listed],
        )
        found = self.adapter.execute(self.request("list", query="versions")).records
        self.assertEqual([first.id], [record.id for record in found])

    def test_contract_update_requires_current_revision(self):
        created = self.create()
        with self.assertRaisesRegex(RecordError, "changed since read") as raised:
            self.adapter.execute(
                self.request(
                    "update",
                    id=created.id,
                    expected_revision="sha256:" + "0" * 64,
                    content="Unsafe overwrite",
                )
            )
        self.assertEqual("stale_revision", raised.exception.code)
        unchanged = self.adapter.execute(self.request("read", id=created.id)).record
        self.assertEqual(created.revision, unchanged.revision)
        self.assertEqual(created.content, unchanged.content)

        updated = self.adapter.execute(
            self.request(
                "update",
                id=created.id,
                expected_revision=created.revision,
                title="Updated compatibility notes",
                content="Revised findings",
            )
        ).record
        self.assertNotEqual(created.revision, updated.revision)
        self.assertEqual("Updated compatibility notes", updated.title)
        self.assertEqual("Revised findings", updated.content)

    def test_contract_create_allocates_and_preserves_identity(self):
        first = self.create(title="Same title")
        second = self.create(title="Same title")
        self.assertEqual("same-title", first.id)
        self.assertEqual("same-title-2", second.id)

        imported = self.create(title="Imported", semantic_id="RESEARCH-0042")
        self.assertEqual("RESEARCH-0042", imported.id)
        with self.assertRaises(RecordError) as raised:
            self.create(title="Duplicate", semantic_id="RESEARCH-0042")
        self.assertEqual("duplicate_id", raised.exception.code)

    def test_contract_archive_retains_but_hides_record(self):
        created = self.create()
        archived = self.adapter.execute(
            self.request(
                "archive",
                id=created.id,
                expected_revision=created.revision,
            )
        ).record
        self.assertTrue(archived.metadata["archived"])
        self.assertEqual([], list(self.adapter.execute(self.request("list")).records))
        read = self.adapter.execute(self.request("read", id=created.id)).record
        self.assertTrue(read.metadata["archived"])
