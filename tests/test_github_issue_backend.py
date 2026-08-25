from pathlib import Path
import importlib.util
import json
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "backends/issue-tracker/github.py"
SPEC = importlib.util.spec_from_file_location("github_issue_backend", MODULE_PATH)
assert SPEC and SPEC.loader
backend_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = backend_module
SPEC.loader.exec_module(backend_module)


BackendError = backend_module.BackendError
GhClient = backend_module.GhClient
GitHubBackend = backend_module.GitHubBackend
LABELS = backend_module.LABELS
Repository = backend_module.Repository


class FakeClient:
    def __init__(self, responder):
        self.responder = responder
        self.calls = []

    def repository(self):
        return Repository("acme/project", "https://github.com/acme/project", "WRITE", True)

    def api(self, endpoint, *, method="GET", payload=None, paginate=False):
        self.calls.append((endpoint, method, payload, paginate))
        return self.responder(endpoint, method, payload, paginate)

    def current_user(self):
        return "octocat"

    def preflight(self):
        return {"repository": "acme/project"}


class GitHubIssueBackendTests(unittest.TestCase):
    def test_gh_client_uses_safe_json_input_and_flattens_pages(self):
        calls = []

        def runner(arguments, input_text):
            calls.append((arguments, input_text))
            return '[[{"number":2}],[{"number":3}]]'

        client = GhClient("acme/project", "octocat", runner)
        result = client.api(
            "/repos/acme/project/issues",
            method="POST",
            payload={"title": "$(unsafe)"},
            paginate=True,
        )
        self.assertEqual([{"number": 2}, {"number": 3}], result)
        self.assertEqual(
            [
                "api",
                "--method",
                "POST",
                "/repos/acme/project/issues",
                "--paginate",
                "--slurp",
                "--input",
                "-",
            ],
            calls[0][0],
        )
        self.assertEqual('{"title":"$(unsafe)"}', calls[0][1])

    def test_explicit_repository_is_a_repo_view_positional_argument(self):
        def runner(arguments, _input_text):
            self.assertEqual(
                [
                    "repo",
                    "view",
                    "acme/project",
                    "--json",
                    "nameWithOwner,url,viewerPermission,hasIssuesEnabled",
                ],
                arguments,
            )
            return json.dumps(
                {
                    "nameWithOwner": "acme/project",
                    "url": "https://github.com/acme/project",
                    "viewerPermission": "WRITE",
                    "hasIssuesEnabled": True,
                }
            )

        self.assertEqual(
            "acme/project", GhClient("acme/project", "octocat", runner).repository().name
        )

    def test_configured_login_must_be_the_active_authenticated_account(self):
        def runner(arguments, _input_text):
            self.assertEqual(
                [
                    "auth",
                    "status",
                    "--hostname",
                    "github.com",
                    "--json",
                    "hosts",
                ],
                arguments,
            )
            return json.dumps(
                {
                    "hosts": {
                        "github.com": [
                            {
                                "active": True,
                                "login": "active-user",
                                "state": "success",
                            },
                            {
                                "active": False,
                                "login": "selected-user",
                                "state": "success",
                            },
                        ]
                    }
                }
            )

        client = GhClient("acme/project", "selected-user", runner)
        with self.assertRaisesRegex(BackendError, "gh auth switch"):
            client.require_login()

    def test_api_identity_must_match_the_configured_active_account(self):
        def runner(arguments, _input_text):
            if arguments[:2] == ["auth", "status"]:
                return json.dumps(
                    {
                        "hosts": {
                            "github.com": [
                                {
                                    "active": True,
                                    "login": "selected-user",
                                    "state": "success",
                                }
                            ]
                        }
                    }
                )
            if arguments == ["api", "--method", "GET", "/user"]:
                return json.dumps({"login": "token-user"})
            raise AssertionError(arguments)

        client = GhClient("acme/project", "selected-user", runner)
        with self.assertRaisesRegex(BackendError, "expected selected-user"):
            client.current_user()

    def test_label_plan_is_reviewable_and_stale_safe(self):
        labels = []

        def responder(endpoint, method, payload, paginate):
            if endpoint.endswith("/labels?per_page=100"):
                return list(labels)
            if method == "POST" and endpoint.endswith("/labels"):
                labels.append({"name": payload["name"], **payload})
                return payload
            raise AssertionError((endpoint, method, payload, paginate))

        backend = GitHubBackend(FakeClient(responder))
        plan = backend.label_plan()
        self.assertEqual(2, plan["schema"])
        self.assertEqual(len(LABELS), len(plan["changes"]))
        planned_names = {item["name"] for item in plan["changes"]}
        self.assertIn("workflow:record:issues", planned_names)
        self.assertIn("workflow:record:specs", planned_names)
        self.assertIn("workflow:issue:bug", planned_names)
        self.assertTrue(all(name.startswith(("workflow:record:", "workflow:issue:")) for name in planned_names))
        self.assertEqual({"create"}, {item["action"] for item in plan["changes"]})
        with self.assertRaisesRegex(BackendError, "does not match"):
            backend.apply_label_plan({**plan, "schema": 1})
        result = backend.apply_label_plan(plan)
        self.assertEqual(len(LABELS), len(result["applied"]))

        stale_plan = {**plan, "changes": [dict(item) for item in plan["changes"]]}
        with self.assertRaisesRegex(BackendError, "label state changed"):
            backend.apply_label_plan(stale_plan)

    def test_create_requires_and_applies_one_semantic_kind(self):
        def responder(endpoint, method, payload, _paginate):
            if endpoint.endswith("/labels/workflow%3Arecord%3Aissues"):
                return {"name": "workflow:record:issues"}
            if endpoint.endswith("/labels/workflow%3Aissue%3Abug"):
                return {"name": "workflow:issue:bug"}
            if method == "POST" and endpoint.endswith("/issues"):
                return {"number": 7, **payload}
            raise AssertionError((endpoint, method, payload))

        backend = GitHubBackend(FakeClient(responder))
        issue = backend.create("Broken result", "Expected X, observed Y", "bug")
        self.assertEqual(
            ["workflow:record:issues", "workflow:issue:bug"], issue["labels"]
        )
        self.assertEqual(7, issue["number"])

    def test_update_preserves_one_kind_and_supports_labels_and_reopen(self):
        def responder(endpoint, method, payload, _paginate):
            if endpoint.endswith("/issues/7") and method == "GET":
                return {
                    "number": 7,
                    "labels": [
                        {"name": "workflow:record:issues"},
                        {"name": "workflow:issue:bug"},
                        {"name": "needs-triage"},
                    ],
                }
            if endpoint.endswith("/labels/workflow%3Aissue%3Aimplementation"):
                return {"name": "workflow:issue:implementation"}
            if endpoint.endswith("/labels/team%3Aplatform"):
                return {"name": "team:platform"}
            if endpoint.endswith("/issues/7") and method == "PATCH":
                return payload
            raise AssertionError((endpoint, method, payload))

        result = GitHubBackend(FakeClient(responder)).update(
            7,
            kind="implementation",
            add_labels=["team:platform"],
            remove_labels=["needs-triage"],
            state="open",
        )
        self.assertEqual(
            ["team:platform", "workflow:issue:implementation", "workflow:record:issues"],
            result["labels"]
        )
        self.assertEqual("reopened", result["state_reason"])

    def test_claim_rejects_an_observed_conflict(self):
        client = FakeClient(
            lambda endpoint, _method, _payload, _paginate: {
                "number": 7,
                "state": "open",
                "assignees": [{"login": "someone-else"}],
            }
        )
        with self.assertRaisesRegex(BackendError, "already claimed"):
            GitHubBackend(client).claim(7)
        self.assertEqual(1, len(client.calls))

    def test_relationship_writes_use_database_ids_and_are_idempotent(self):
        children = []
        blockers = []

        def responder(endpoint, method, payload, _paginate):
            if endpoint.endswith("/issues/20") and method == "GET":
                return {"id": 2000, "number": 20, "assignees": []}
            if endpoint.endswith("/issues/30") and method == "GET":
                return {"id": 3000, "number": 30, "assignees": []}
            if endpoint.endswith("/issues/10/sub_issues?per_page=100"):
                return list(children)
            if endpoint.endswith("/issues/20/dependencies/blocked_by?per_page=100"):
                return list(blockers)
            if endpoint.endswith("/issues/10/sub_issues") and method == "POST":
                children.append({"id": payload["sub_issue_id"], "number": 20})
                return {}
            if endpoint.endswith("/issues/20/dependencies/blocked_by") and method == "POST":
                blockers.append({"id": payload["issue_id"], "number": 30})
                return {}
            raise AssertionError((endpoint, method, payload))

        client = FakeClient(responder)
        backend = GitHubBackend(client)
        self.assertTrue(backend.add_parent(10, 20)["changed"])
        self.assertFalse(backend.add_parent(10, 20)["changed"])
        self.assertTrue(backend.add_blocker(20, 30)["changed"])
        self.assertFalse(backend.add_blocker(20, 30)["changed"])
        writes = [call for call in client.calls if call[1] == "POST"]
        self.assertEqual({"sub_issue_id": 2000}, writes[0][2])
        self.assertEqual({"issue_id": 3000}, writes[1][2])

    def test_frontier_is_stable_and_cancelled_blockers_do_not_satisfy(self):
        children = [
            {"number": 14, "state": "open", "assignees": []},
            {"number": 11, "state": "open", "assignees": []},
            {"number": 12, "state": "open", "assignees": [{"login": "claimed"}]},
            {"number": 13, "state": "closed", "assignees": []},
        ]
        blockers = {
            11: [{"state": "closed", "state_reason": "completed"}],
            14: [{"state": "closed", "state_reason": "not_planned"}],
        }

        def responder(endpoint, _method, _payload, _paginate):
            if endpoint.endswith("/issues/10/sub_issues?per_page=100"):
                return children
            for number, values in blockers.items():
                if endpoint.endswith(
                    f"/issues/{number}/dependencies/blocked_by?per_page=100"
                ):
                    return values
            raise AssertionError(endpoint)

        result = GitHubBackend(FakeClient(responder)).frontier(10)
        self.assertEqual([11], [issue["number"] for issue in result])

    def test_resolve_and_cancel_use_distinct_close_reasons(self):
        calls = []

        def responder(endpoint, method, payload, _paginate):
            calls.append((endpoint, method, payload))
            if method == "GET":
                return {"number": 9, "state": "open"}
            return {"number": 9, **(payload or {})}

        backend = GitHubBackend(FakeClient(responder))
        backend.resolve(9, "Delivered")
        backend.cancel(9, "Out of scope")
        close_payloads = [payload for _endpoint, method, payload in calls if method == "PATCH"]
        self.assertEqual(
            [
                {"state": "closed", "state_reason": "completed"},
                {"state": "closed", "state_reason": "not_planned"},
            ],
            close_payloads,
        )


if __name__ == "__main__":
    unittest.main()
