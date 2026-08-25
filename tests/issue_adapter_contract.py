"""Reusable behavior checks for issue-capable semantic record adapters."""

from __future__ import annotations

from contract import IssueRequest, RecordError


class IssueAdapterContract:
    adapter = None
    backend = ""
    issue_destination = {}

    def issue_request(self, operation: str, **values):
        return IssueRequest(
            operation=operation,
            backend=self.backend,
            destination=self.issue_destination,
            **values,
        )

    def create_issue(self, title="Deliver behavior", body="## What to build\n\nOutcome", kind="implementation"):
        response = self.adapter.execute_issue(
            self.issue_request(
                "create",
                title=title,
                body=body,
                kind=kind,
                labels=("phase-1",),
            )
        )
        self.assertIsNotNone(response.issue)
        return response.issue

    def mutate(self, operation, issue, **values):
        return self.adapter.execute_issue(
            self.issue_request(
                operation,
                id=issue.id,
                expected_revision=issue.revision,
                **values,
            )
        ).issue

    def test_issue_contract_create_read_list_and_update(self):
        created = self.create_issue()
        read = self.adapter.execute_issue(
            self.issue_request("read", id=created.id)
        ).issue
        self.assertEqual(created.as_dict(), read.as_dict())
        self.assertEqual("open", created.status)
        self.assertEqual(self.backend, created.reference.backend)

        listed = self.adapter.execute_issue(
            self.issue_request("list", kind="implementation", labels=("phase-1",))
        ).issues
        self.assertEqual([created.id], [issue.id for issue in listed])
        found = self.adapter.execute_issue(
            self.issue_request("list", query="Outcome")
        ).issues
        self.assertEqual([created.id], [issue.id for issue in found])

        updated = self.mutate(
            "update",
            created,
            title="Deliver revised behavior",
            body="## What to build\n\nRevised outcome",
            labels=("phase-1", "reviewed"),
        )
        self.assertEqual("Deliver revised behavior", updated.title)
        self.assertIn("Revised outcome", updated.body)
        self.assertEqual(("phase-1", "reviewed"), updated.labels)
        self.assertNotEqual(created.revision, updated.revision)

    def test_issue_contract_stale_mutations_do_not_write(self):
        issue = self.create_issue()
        with self.assertRaises(RecordError) as raised:
            self.adapter.execute_issue(
                self.issue_request(
                    "comment",
                    id=issue.id,
                    expected_revision="sha256:" + "0" * 64,
                    body="Unsafe comment",
                )
            )
        self.assertEqual("stale_revision", raised.exception.code)
        unchanged = self.adapter.execute_issue(
            self.issue_request("read", id=issue.id)
        ).issue
        self.assertEqual(issue.revision, unchanged.revision)
        self.assertNotIn("Unsafe comment", unchanged.body)

    def test_issue_contract_comment_claim_resolve_and_cancel(self):
        issue = self.create_issue()
        commented = self.mutate(
            "comment", issue, body="Chronological evidence", assignee="reviewer"
        )
        self.assertIn("Chronological evidence", commented.body)
        self.assertIn("reviewer", commented.body)

        claimed = self.mutate("claim", commented, assignee="agent")
        self.assertEqual("claimed", claimed.status)
        self.assertEqual("agent", claimed.assignee)
        with self.assertRaises(RecordError) as raised:
            self.mutate("claim", claimed, assignee="other")
        self.assertEqual("claim_conflict", raised.exception.code)

        resolved = self.mutate("resolve", claimed, body="Delivered and verified")
        self.assertEqual("resolved", resolved.status)
        self.assertIn("Delivered and verified", resolved.body)

        cancelled = self.create_issue(title="No longer needed")
        cancelled = self.mutate("cancel", cancelled, body="Removed from scope")
        self.assertEqual("cancelled", cancelled.status)
        self.assertIn("Removed from scope", cancelled.body)

    def test_issue_contract_parent_block_and_frontier(self):
        parent = self.create_issue(title="Initiative map", kind="initiative")
        first = self.create_issue(title="First child")
        second = self.create_issue(title="Second child")
        blocker = self.create_issue(title="Required fact", kind="research")

        first = self.mutate("parent", first, parent_id=parent.id)
        second = self.mutate("parent", second, parent_id=parent.id)
        second = self.mutate("block", second, blocker_id=blocker.id)
        repeated = self.mutate("block", second, blocker_id=blocker.id)
        self.assertEqual((blocker.id,), repeated.blocked_by)
        with self.assertRaises(RecordError) as parent_cycle:
            self.mutate("parent", parent, parent_id=first.id)
        self.assertEqual("invalid_relationship", parent_cycle.exception.code)
        with self.assertRaises(RecordError) as blocker_cycle:
            self.mutate("block", blocker, blocker_id=second.id)
        self.assertEqual("invalid_relationship", blocker_cycle.exception.code)

        frontier = self.adapter.execute_issue(
            self.issue_request("frontier", id=parent.id)
        ).issues
        self.assertEqual([first.id], [issue.id for issue in frontier])

        blocker = self.mutate("resolve", blocker, body="Fact established")
        frontier = self.adapter.execute_issue(
            self.issue_request("frontier", id=parent.id)
        ).issues
        self.assertEqual([first.id, second.id], [issue.id for issue in frontier])

        first = self.mutate("claim", first, assignee="agent")
        frontier = self.adapter.execute_issue(
            self.issue_request("frontier", id=parent.id)
        ).issues
        self.assertEqual([second.id], [issue.id for issue in frontier])

        second = self.mutate("block", repeated, blocker_id=blocker.id, remove=True)
        second = self.mutate("parent", second, remove=True)
        self.assertEqual((), second.blocked_by)
        self.assertIsNone(second.parent)

    def test_issue_contract_allocates_stable_ids(self):
        first = self.create_issue(title="First")
        second = self.create_issue(title="Second")
        self.assertRegex(first.id, r"ISSUE-[0-9]{4,}")
        self.assertEqual(int(first.id.split("-")[1]) + 1, int(second.id.split("-")[1]))
