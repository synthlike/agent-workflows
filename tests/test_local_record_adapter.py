from concurrent.futures import ThreadPoolExecutor
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
    RecordError,
    RecordReference,
    RecordRequest,
    RecordResponse,
    StoredRecord,
)
from tests.issue_adapter_contract import IssueAdapterContract  # noqa: E402
from tests.record_adapter_contract import RecordAdapterContract  # noqa: E402

SPEC = importlib.util.spec_from_file_location(
    "local_markdown_record_adapter", BACKEND / "local-markdown.py"
)
assert SPEC and SPEC.loader
local_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = local_module
SPEC.loader.exec_module(local_module)
LocalMarkdownAdapter = local_module.LocalMarkdownAdapter


class LocalRecordAdapterTests(
    IssueAdapterContract,
    RecordAdapterContract,
    unittest.TestCase,
):
    backend = "local"
    record_type = "research"
    destination = {"path": "docs/research"}
    issue_destination = {"root": ".project"}

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        counter = iter(range(1, 100))
        self.adapter = LocalMarkdownAdapter(
            self.root,
            self.backend,
            clock=lambda: f"2026-08-25T00:00:{next(counter):02d}Z",
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_destination_is_lazy_and_repository_contained(self):
        destination = self.root / "docs/research"
        self.assertFalse(destination.exists())
        self.assertEqual([], list(self.adapter.execute(self.request("list")).records))
        self.assertFalse(destination.exists())
        self.create()
        self.assertTrue(destination.is_dir())

        with self.assertRaises(RecordError) as raised:
            self.adapter.execute(
                RecordRequest(
                    operation="list",
                    backend=self.backend,
                    record_type=self.record_type,
                    destination={"path": "../outside"},
                )
            )
        self.assertEqual("invalid_destination", raised.exception.code)

    def test_all_non_issue_record_types_and_prefixes(self):
        destinations = {
            "domain": {"path": "docs/domain"},
            "arps": {"path": "docs/decisions", "prefix": "ARP"},
            "rfcs": {"path": "docs/rfcs", "prefix": "RFC"},
            "specs": {"path": "docs/specs"},
            "meetings": {"path": "docs/meetings"},
            "research": {"path": "docs/research"},
            "questionnaires": {"path": "docs/questionnaires"},
            "technical_baselines": {"path": "docs/engineering"},
            "problem_framing": {"path": "docs/product"},
            "prototypes": {"path": "docs/prototypes"},
            "handoffs": {"path": ".agents/handoffs"},
        }
        created = {}
        for record_type, destination in destinations.items():
            with self.subTest(record_type=record_type):
                response = self.adapter.execute(
                    RecordRequest(
                        operation="create",
                        backend=self.backend,
                        record_type=record_type,
                        destination=destination,
                        title=f"{record_type} record",
                        content="Canonical content",
                    )
                )
                created[record_type] = response.record
                read = self.adapter.execute(
                    RecordRequest(
                        operation="read",
                        backend=self.backend,
                        record_type=record_type,
                        destination=destination,
                        id=response.record.id,
                    )
                ).record
                self.assertEqual(response.record.as_dict(), read.as_dict())
        self.assertEqual("ARP-0001", created["arps"].id)
        self.assertEqual("RFC-0001", created["rfcs"].id)

    def test_existing_plain_markdown_records_remain_readable_without_migration(self):
        research = self.root / "docs/research"
        research.mkdir(parents=True)
        path = research / "platform-facts.md"
        original = "# Platform facts\n\nVerified behavior.\n"
        path.write_text(original)
        record = self.adapter.execute(
            RecordRequest(
                operation="read",
                backend=self.backend,
                record_type="research",
                destination={"path": "docs/research"},
                id="platform-facts",
            )
        ).record
        self.assertEqual("Platform facts", record.title)
        self.assertEqual(original, record.content)
        self.assertTrue(record.metadata["legacy"])
        self.assertEqual(original, path.read_text())

        decisions = self.root / "docs/decisions"
        decisions.mkdir(parents=True)
        decision = decisions / "ARP-0042-existing-choice.md"
        decision.write_text("# Existing choice\n\nDecision context.\n")
        existing = self.adapter.execute(
            RecordRequest(
                operation="read",
                backend=self.backend,
                record_type="arps",
                destination={"path": "docs/decisions", "prefix": "ARP"},
                id="ARP-0042",
            )
        ).record
        self.assertEqual("ARP-0042", existing.id)
        created = self.adapter.execute(
            RecordRequest(
                operation="create",
                backend=self.backend,
                record_type="arps",
                destination={"path": "docs/decisions", "prefix": "ARP"},
                title="Next choice",
                content="# Next choice\n",
            )
        ).record
        self.assertEqual("ARP-0043", created.id)

    def test_existing_local_issue_shape_remains_readable(self):
        issue_dir = self.root / ".project/issues"
        issue_dir.mkdir(parents=True)
        path = issue_dir / "ISSUE-0099-existing.md"
        path.write_text(
            """---
id: ISSUE-0099
title: Existing issue
kind: task
status: open
created: 2026-08-25
assignee:
parent:
blocked_by: []
labels: [existing, local]
---

# Existing issue

## Question or work

Preserve this shape.

## Comments

## Resolution
"""
        )
        issue = self.adapter.execute_issue(
            self.issue_request("read", id="ISSUE-0099")
        ).issue
        self.assertEqual("Existing issue", issue.title)
        self.assertEqual(("existing", "local"), issue.labels)
        self.assertEqual("open", issue.status)

    def test_malformed_record_fails_listing(self):
        destination = self.root / "docs/research"
        destination.mkdir(parents=True)
        (destination / "broken.md").write_text("No title heading\n")
        with self.assertRaises(RecordError) as raised:
            self.adapter.execute(self.request("list"))
        self.assertEqual("malformed_record", raised.exception.code)

    def test_broken_issue_relationship_is_reported(self):
        child = self.create_issue(title="Dependent issue")
        blocker = self.create_issue(title="Blocking issue")
        child = self.mutate("block", child, blocker_id=blocker.id)
        (self.root / blocker.reference.id).unlink()
        with self.assertRaises(RecordError) as raised:
            self.adapter.execute_issue(self.issue_request("read", id=child.id))
        self.assertEqual("broken_reference", raised.exception.code)

    def test_concurrent_local_allocations_are_unique(self):
        def create_record(_index):
            adapter = LocalMarkdownAdapter(self.root, self.backend)
            return adapter.execute(
                RecordRequest(
                    operation="create",
                    backend=self.backend,
                    record_type="research",
                    destination=self.destination,
                    title="Concurrent title",
                    content="Findings",
                )
            ).record.id

        with ThreadPoolExecutor(max_workers=6) as executor:
            record_ids = list(executor.map(create_record, range(12)))
        self.assertEqual(12, len(set(record_ids)))

        def create_issue(index):
            adapter = LocalMarkdownAdapter(self.root, self.backend)
            return adapter.execute_issue(
                self.issue_request(
                    "create",
                    title=f"Concurrent issue {index}",
                    body="Outcome",
                    kind="implementation",
                )
            ).issue.id

        with ThreadPoolExecutor(max_workers=6) as executor:
            issue_ids = list(executor.map(create_issue, range(12)))
        self.assertEqual(12, len(set(issue_ids)))

    def test_contract_shapes_are_json_serializable(self):
        reference = RecordReference("local", "docs/research/item.md", "Item", "docs/research/item.md")
        record = StoredRecord(
            record_type="research",
            id="item",
            title="Item",
            content="Findings",
            revision="sha256:" + "0" * 64,
            reference=reference,
            metadata={"archived": False},
        )
        response = RecordResponse(record=record)
        parsed = json.loads(json.dumps(response.as_dict()))
        self.assertTrue(parsed["ok"])
        self.assertEqual("local", parsed["record"]["reference"]["backend"])
        error = RecordError("stale_revision", "changed")
        self.assertEqual(
            {"code": "stale_revision", "message": "changed"}, error.as_dict()
        )

    def test_request_validation_is_portable(self):
        with self.assertRaises(RecordError) as raised:
            RecordRequest(
                operation="update",
                backend="local",
                record_type="research",
                destination=self.destination,
                id="item",
                content="Changed",
            ).validate()
        self.assertEqual("invalid_request", raised.exception.code)


if __name__ == "__main__":
    unittest.main()
