from __future__ import annotations

from pathlib import Path
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RECORD_STORE = ROOT / "backends/record-store"
sys.path.insert(0, str(RECORD_STORE))
from contract import RecordError, RecordRequest  # noqa: E402
from tests.record_adapter_contract import RecordAdapterContract  # noqa: E402

SPEC = importlib.util.spec_from_file_location("bear_record_backend", RECORD_STORE / "bear.py")
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


class FakeBearClient:
    def __init__(self):
        self.notes: dict[str, dict] = {}
        self.next_id = 1
        self.calls = []
        self.page_size = 2
        self.race_before_overwrite = False

    @staticmethod
    def hash(content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()

    @staticmethod
    def metadata(note: dict) -> dict:
        return {
            "attachments": list(note.get("attachments", [])),
            "created": "2026-08-25T00:00:00Z",
            "done": 0,
            "id": note["id"],
            "length": len(note["content"].encode()),
            "location": note.get("location", "notes"),
            "locked": False,
            "modified": note.get("modified", "2026-08-25T00:00:00Z"),
            "pins": [],
            "tags": list(note["tags"]),
            "title": note["title"],
            "todos": 0,
        }

    def call_tool(self, name: str, arguments: dict) -> dict:
        self.calls.append((name, dict(arguments)))
        if name == "create_note":
            note_id = f"BEAR/{self.next_id}"
            self.next_id += 1
            note = {
                "id": note_id,
                "title": arguments["title"],
                "content": arguments["content"],
                "tags": list(arguments["tags"]),
                "location": "notes",
                "attachments": [],
            }
            self.notes[note_id] = note
            return {**self.metadata(note), "content": note["content"]}
        if name == "get_note":
            note = self.notes.get(arguments["id"])
            if note is None:
                raise module.BearError("not_found", "note missing")
            return {"metadata": self.metadata(note)}
        if name == "read_note_content":
            note = self.notes.get(arguments["id"])
            if note is None:
                raise module.BearError("not_found", "note missing")
            return {"content": note["content"], "hash": self.hash(note["content"])}
        if name == "list_notes":
            matching = [
                note for note in self.notes.values()
                if arguments["tag"] in note["tags"]
                and arguments["location"] in {"all", note.get("location", "notes")}
            ]
            matching.sort(key=lambda note: note["title"])
            offset = arguments["offset"]
            limit = min(arguments["limit"], self.page_size)
            page = matching[offset:offset + limit]
            return {"metadata": [self.metadata(note) for note in page], "total": len(matching)}
        if name == "overwrite_note":
            note = self.notes.get(arguments["id"])
            if note is None:
                raise module.BearError("not_found", "note missing")
            if self.race_before_overwrite:
                self.race_before_overwrite = False
                self.external_edit(arguments["id"], "\nconcurrent")
            if arguments["baseHash"] != self.hash(note["content"]):
                raise module.BearError("stale_revision", "baseHash is stale")
            note["content"] = arguments["content"]
            heading = re.search(r"(?m)^# (.+)$", note["content"])
            note["title"] = heading.group(1) if heading else note["title"]
            note["modified"] = "2026-08-25T00:00:01Z"
            return {"changedMetadata": self.metadata(note)}
        raise AssertionError(f"unexpected tool: {name}")

    def external_edit(self, note_id: str, suffix: str = "\nexternal") -> None:
        marker = f"\n\n{module.TAG_MARKER}"
        self.notes[note_id]["content"] = self.notes[note_id]["content"].replace(
            marker, suffix + marker, 1
        )


class BearRecordAdapterTests(RecordAdapterContract, unittest.TestCase):
    backend = "bear-notes"
    record_type = "research"
    destination = {"tag": "research"}

    def setUp(self) -> None:
        self.client = FakeBearClient()
        self.adapter = module.BearRecordAdapter(
            self.client, self.backend, "agent-workflows/project"
        )

    def test_all_non_issue_record_types_and_managed_framing(self) -> None:
        for record_type in sorted(module.NON_ISSUE_RECORD_TYPES):
            with self.subTest(record_type=record_type):
                destination = {"tag": record_type}
                created = self.adapter.execute(
                    RecordRequest(
                        operation="create",
                        backend=self.backend,
                        record_type=record_type,
                        destination=destination,
                        title=f"{record_type} title",
                        content="Canonical content",
                    )
                ).record
                self.assertEqual(record_type, created.record_type)
                self.assertTrue(created.revision.startswith(module.REVISION_PREFIX))
                native = self.client.notes[created.reference.id]
                self.assertTrue(native["content"].startswith("<!-- agent-workflows-record:"))
                self.assertIn(f"# {record_type} title\n", native["content"])
                self.assertTrue(native["content"].endswith(
                    f"{module.TAG_MARKER}\n#agent-workflows/project #agent-workflows/project/{record_type}"
                ))
                self.assertEqual(
                    {"agent-workflows/project", f"agent-workflows/project/{record_type}"},
                    set(native["tags"]),
                )

    def test_list_paginates_and_archive_remains_directly_readable(self) -> None:
        records = [self.create(title=f"Record {number}") for number in range(5)]
        self.client.calls.clear()
        listed = self.adapter.execute(self.request("list")).records
        self.assertEqual(sorted(record.id for record in records), [record.id for record in listed])
        self.assertGreaterEqual(
            len([call for call in self.client.calls if call[0] == "list_notes"]), 3
        )
        archived = self.adapter.execute(
            self.request(
                "archive", id=records[0].id, expected_revision=records[0].revision
            )
        ).record
        self.assertTrue(archived.metadata["archived"])
        self.assertNotIn(
            records[0].id,
            [record.id for record in self.adapter.execute(self.request("list")).records],
        )
        self.assertEqual(
            records[0].id,
            self.adapter.execute(self.request("read", id=records[0].id)).record.id,
        )

    def test_archived_and_duplicate_owners_still_block_semantic_id_reuse(self) -> None:
        created = self.create(semantic_id="RESEARCH-0042")
        self.adapter.execute(
            self.request(
                "archive", id=created.id, expected_revision=created.revision
            )
        )
        with self.assertRaises(RecordError) as archived_collision:
            self.create(semantic_id="RESEARCH-0042")
        self.assertEqual("duplicate_id", archived_collision.exception.code)

        duplicate = dict(self.client.notes[created.reference.id])
        duplicate["id"] = "BEAR/duplicate"
        self.client.notes[duplicate["id"]] = duplicate
        with self.assertRaises(RecordError) as owners:
            self.adapter.execute(self.request("read", id=created.id))
        self.assertEqual("duplicate_id", owners.exception.code)

    def test_provider_native_reference_is_stable_and_encoded(self) -> None:
        created = self.create()
        self.assertEqual("BEAR/1", created.reference.id)
        self.assertEqual(
            "bear://x-callback-url/open-note?id=BEAR%2F1", created.reference.href
        )

    def test_external_change_invalidates_revision_without_overwrite(self) -> None:
        created = self.create()
        self.client.external_edit(created.reference.id)
        overwrite_count = len([call for call in self.client.calls if call[0] == "overwrite_note"])
        with self.assertRaises(RecordError) as raised:
            self.adapter.execute(
                self.request(
                    "update",
                    id=created.id,
                    expected_revision=created.revision,
                    content="unsafe",
                )
            )
        self.assertEqual("stale_revision", raised.exception.code)
        self.assertEqual(
            overwrite_count,
            len([call for call in self.client.calls if call[0] == "overwrite_note"]),
        )

    def test_base_hash_closes_the_race_after_adapter_revision_check(self) -> None:
        created = self.create()
        self.client.race_before_overwrite = True
        with self.assertRaises(RecordError) as raised:
            self.adapter.execute(
                self.request(
                    "update",
                    id=created.id,
                    expected_revision=created.revision,
                    content="unsafe",
                )
            )
        self.assertEqual("stale_revision", raised.exception.code)
        self.assertIn("concurrent", self.client.notes[created.reference.id]["content"])
        self.assertNotIn("unsafe", self.client.notes[created.reference.id]["content"])

    def test_protocol_failure_maps_to_portable_io_error_without_mutation(self) -> None:
        def fail(_name, _arguments):
            raise module.BearError("protocol_error", "invalid JSON-RPC response")

        self.client.call_tool = fail
        with self.assertRaises(RecordError) as raised:
            self.adapter.execute(self.request("list"))
        self.assertEqual("io_error", raised.exception.code)
        self.assertEqual({}, self.client.notes)

    def test_malformed_managed_note_and_attachments_fail_without_write(self) -> None:
        created = self.create()
        self.client.notes[created.reference.id]["content"] = "not managed"
        with self.assertRaises(RecordError) as malformed:
            self.adapter.execute(self.request("read", id=created.id))
        self.assertEqual("malformed_record", malformed.exception.code)

        self.setUp()
        created = self.create()
        self.client.notes[created.reference.id]["attachments"] = ["file.pdf"]
        current = self.adapter.execute(self.request("read", id=created.id)).record
        with self.assertRaises(RecordError) as attached:
            self.adapter.execute(
                self.request(
                    "update",
                    id=current.id,
                    expected_revision=current.revision,
                    content="would remove attachment",
                )
            )
        self.assertEqual("invalid_state", attached.exception.code)

    def test_render_reference_cli_does_not_launch_bear_and_rejects_malformed_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "reference.json"
            reference.write_text(json.dumps({
                "backend": "other", "id": "42", "title": "Other", "href": "https://example.test/42"
            }))
            command = [
                sys.executable, str(RECORD_STORE / "bear.py"),
                "--command", "/missing/bearcli", "--workspace", "agent-workflows/project",
                "--backend", self.backend, "render-reference", "--reference-file", str(reference),
            ]
            completed = subprocess.run(command, text=True, capture_output=True, check=False)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("[Other](<https://example.test/42>)", json.loads(completed.stdout)["rendered"])

            reference.write_text("not-json")
            malformed = subprocess.run(command, text=True, capture_output=True, check=False)
            self.assertEqual(1, malformed.returncode)
            self.assertEqual("malformed_reference", json.loads(malformed.stdout)["error"]["code"])

    def test_destination_and_issue_route_are_rejected(self) -> None:
        with self.assertRaises(RecordError) as destination:
            self.create(destination={"tag": "#research"})
        self.assertEqual("invalid_destination", destination.exception.code)
        with self.assertRaises(RecordError) as issue:
            self.adapter.execute(
                RecordRequest(
                    operation="create",
                    backend=self.backend,
                    record_type="issues",
                    destination={"tag": "issues"},
                    title="Issue",
                    content="Body",
                )
            )
        self.assertEqual("unsupported_record_type", issue.exception.code)
        self.assertFalse(hasattr(self.adapter, "execute_issue"))


if __name__ == "__main__":
    unittest.main()
