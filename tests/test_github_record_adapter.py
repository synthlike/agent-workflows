from __future__ import annotations

from pathlib import Path
import importlib.util
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
RECORD_STORE = ROOT / "backends/record-store"
sys.path.insert(0, str(RECORD_STORE))
from contract import RecordError  # noqa: E402
from tests.issue_adapter_contract import IssueAdapterContract  # noqa: E402
from tests.record_adapter_contract import RecordAdapterContract  # noqa: E402

MODULE_PATH = ROOT / "backends/record-store/github.py"
SPEC = importlib.util.spec_from_file_location("github_portable_backend", MODULE_PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


GitHubRecordAdapter = module.GitHubRecordAdapter
LABELS = module.LABELS
Repository = module.Repository
BackendError = module.BackendError


class StatefulGitHubClient:
    def __init__(self):
        self.issues = {}
        self.comments = {}
        self.children = {}
        self.blockers = {}
        self.labels = {
            name: {"name": name, **settings} for name, settings in LABELS.items()
        }
        self.labels.update(
            {
                name: {"name": name, "color": "EEEEEE", "description": "test"}
                for name in ("phase-1", "reviewed")
            }
        )
        self.next_number = 1
        self.clock = 0
        self.calls = []

    def repository(self):
        return Repository("acme/project", "https://github.com/acme/project", "WRITE", True)

    def current_user(self):
        return "octocat"

    def preflight(self):
        return {"repository": "acme/project"}

    def _touch(self, issue):
        self.clock += 1
        issue["updated_at"] = f"2026-08-25T00:00:{self.clock:02d}Z"

    def _issue_by_database_id(self, database_id):
        return next(issue for issue in self.issues.values() if issue["id"] == database_id)

    def _reachable(self, graph, start, target):
        if start == target:
            return True
        return any(self._reachable(graph, item, target) for item in graph.get(start, []))

    def api(self, endpoint, *, method="GET", payload=None, paginate=False):
        self.calls.append((endpoint, method, payload, paginate))
        suffix = endpoint.removeprefix("/repos/acme/project")
        collection = suffix.removesuffix("?per_page=100")

        if collection == "/labels" and method == "GET":
            return list(self.labels.values())
        if suffix.startswith("/labels/") and method == "GET":
            from urllib.parse import unquote

            return self.labels[unquote(suffix.split("/labels/", 1)[1])]
        if suffix == "/labels" and method == "POST":
            self.labels[payload["name"]] = dict(payload)
            return payload

        if collection.startswith("/issues?state=") and method == "GET":
            state = collection.split("state=", 1)[1].split("&", 1)[0]
            values = list(self.issues.values())
            if state != "all":
                values = [issue for issue in values if issue["state"] == state]
            return [*values, {"number": 999, "pull_request": {}, "labels": []}]

        if suffix == "/issues" and method == "POST":
            number = self.next_number
            self.next_number += 1
            issue = {
                "id": number * 100,
                "number": number,
                "title": payload["title"],
                "body": payload.get("body") or "",
                "labels": [{"name": name} for name in payload.get("labels", [])],
                "state": "open",
                "state_reason": None,
                "assignees": [],
                "created_at": "2026-08-25T00:00:00Z",
                "html_url": f"https://github.com/acme/project/issues/{number}",
            }
            self._touch(issue)
            self.issues[number] = issue
            self.comments[number] = []
            self.children[number] = []
            self.blockers[number] = []
            return issue

        match = module.re.fullmatch(r"/issues/(\d+)(.*)", collection)
        if not match:
            raise AssertionError((endpoint, method, payload, paginate))
        number = int(match.group(1))
        tail = match.group(2)
        issue = self.issues[number]

        if not tail and method == "GET":
            return issue
        if not tail and method == "PATCH":
            for key, value in payload.items():
                if key == "labels":
                    issue[key] = [{"name": name} for name in value]
                else:
                    issue[key] = value
            self._touch(issue)
            return issue
        if tail == "/comments" and method == "GET":
            return list(self.comments[number])
        if tail == "/comments" and method == "POST":
            comment = {
                "id": len(self.comments[number]) + 1,
                "body": payload["body"],
                "user": {"login": "octocat"},
            }
            self.comments[number].append(comment)
            return comment
        if tail == "/assignees" and method == "POST":
            issue["assignees"] = [{"login": login} for login in payload["assignees"]]
            self._touch(issue)
            return issue
        if tail == "/parent" and method == "GET":
            for parent, child_numbers in self.children.items():
                if number in child_numbers:
                    return self.issues[parent]
            return None
        if tail == "/sub_issues" and method == "GET":
            return [self.issues[item] for item in self.children[number]]
        if tail == "/sub_issues" and method == "POST":
            child = self._issue_by_database_id(payload["sub_issue_id"])["number"]
            if self._reachable(self.children, child, number):
                raise BackendError("parent relationship would create a cycle")
            if child not in self.children[number]:
                self.children[number].append(child)
            return {}
        if tail == "/sub_issue" and method == "DELETE":
            child = self._issue_by_database_id(payload["sub_issue_id"])["number"]
            if child in self.children[number]:
                self.children[number].remove(child)
            return {}
        if tail == "/dependencies/blocked_by" and method == "GET":
            return [self.issues[item] for item in self.blockers[number]]
        if tail == "/dependencies/blocked_by" and method == "POST":
            blocker = self._issue_by_database_id(payload["issue_id"])["number"]
            if self._reachable(self.blockers, blocker, number):
                raise BackendError("block relationship would create a cycle")
            if blocker not in self.blockers[number]:
                self.blockers[number].append(blocker)
            return {}
        blocker_match = module.re.fullmatch(r"/dependencies/blocked_by/(\d+)", tail)
        if blocker_match and method == "DELETE":
            blocker = self._issue_by_database_id(int(blocker_match.group(1)))["number"]
            if blocker in self.blockers[number]:
                self.blockers[number].remove(blocker)
            return {}
        raise AssertionError((endpoint, method, payload, paginate))


class GitHubRecordAdapterTests(
    IssueAdapterContract,
    RecordAdapterContract,
    unittest.TestCase,
):
    backend = "github-main"
    record_type = "research"
    destination = {"label": "workflow:record:research"}
    issue_destination = {"label": "workflow:record:issues"}

    def setUp(self):
        self.client = StatefulGitHubClient()
        self.adapter = GitHubRecordAdapter(self.client, self.backend)

    def test_portable_cli_requires_explicit_route_inputs(self):
        args = module.build_parser().parse_args(
            [
                "--repo", "acme/project",
                "--login", "octocat",
                "--backend", "github-main",
                "--destination-label", "workflow:record:research",
                "record-list",
                "--record-type", "research",
                "--query", "compatibility",
            ]
        )
        self.assertEqual("github-main", args.backend)
        self.assertEqual("workflow:record:research", args.destination_label)
        self.assertEqual("record-list", args.command)

    def test_all_non_issue_record_types_use_one_managed_label_and_close(self):
        for record_type in sorted(module.RECORD_TYPES - {"issues"}):
            with self.subTest(record_type=record_type):
                self.record_type = record_type
                self.destination = {"label": f"workflow:record:{record_type}"}
                record = self.create(title=f"{record_type} record", content="Canonical")
                native = self.client.issues[int(record.reference.id)]
                managed = {
                    item["name"]
                    for item in native["labels"]
                    if item["name"].startswith("workflow:record:")
                }
                self.assertEqual({f"workflow:record:{record_type}"}, managed)
                self.assertEqual(("closed", "completed"), (native["state"], native["state_reason"]))

    def test_non_issue_records_close_completed_and_search_excludes_pull_requests(self):
        record = self.create(title="Published fact", content="Canonical evidence")
        native = self.client.issues[int(record.reference.id)]
        self.assertEqual("closed", native["state"])
        self.assertEqual("completed", native["state_reason"])
        found = self.adapter.execute(
            self.request("list", query="Canonical evidence")
        ).records
        self.assertEqual([record.id], [item.id for item in found])

    def test_external_canonical_change_invalidates_revision_without_write(self):
        record = self.create()
        native = self.client.issues[int(record.reference.id)]
        native["body"] += "\nexternal change"
        self.client._touch(native)
        writes_before = len([call for call in self.client.calls if call[1] == "PATCH"])
        with self.assertRaises(RecordError) as raised:
            self.adapter.execute(
                self.request(
                    "update",
                    id=record.id,
                    expected_revision=record.revision,
                    content="unsafe overwrite",
                )
            )
        self.assertEqual("stale_revision", raised.exception.code)
        writes_after = len([call for call in self.client.calls if call[1] == "PATCH"])
        self.assertEqual(writes_before, writes_after)
        self.assertIn("external change", native["body"])

    def test_destination_and_managed_label_shape_are_strict(self):
        with self.assertRaises(RecordError) as raised:
            self.adapter.execute(
                self.request(
                    "create",
                    title="Wrong route",
                    content="Content",
                    destination={"label": "workflow:record:domain"},
                )
            )
        self.assertEqual("invalid_destination", raised.exception.code)

        issue = self.create_issue()
        labels = {
            item["name"] for item in self.client.issues[int(issue.reference.id)]["labels"]
        }
        self.assertEqual(
            {"workflow:record:issues", "workflow:issue:implementation", "phase-1"},
            labels,
        )
        native = self.client.issues[int(issue.reference.id)]
        native["labels"].append({"name": "workflow:issue:bug"})
        with self.assertRaises(RecordError) as malformed:
            self.adapter.execute_issue(self.issue_request("read", id=issue.id))
        self.assertEqual("malformed_record", malformed.exception.code)


if __name__ == "__main__":
    unittest.main()
