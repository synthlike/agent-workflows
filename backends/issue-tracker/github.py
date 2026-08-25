#!/usr/bin/env python3
"""Deterministic GitHub Cloud issue-backend operations through the gh CLI."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable
from urllib.parse import quote


LABELS = {
    "initiative": {
        "color": "5319E7",
        "description": "Parent map for a bounded initiative",
    },
    "bug": {
        "color": "D73A4A",
        "description": "Accepted defect with observable incorrect behavior",
    },
    "implementation": {
        "color": "0075CA",
        "description": "Executable vertical delivery slice",
    },
    "clarification": {
        "color": "FBCA04",
        "description": "Question requiring a human decision",
    },
    "research": {
        "color": "0E8A16",
        "description": "Focused external fact-finding question",
    },
    "prototype": {
        "color": "D4C5F9",
        "description": "Question answered through a disposable concrete artifact",
    },
    "prerequisite": {
        "color": "BFDADC",
        "description": "Enabling action that does not implement the destination",
    },
}
MANAGED_LABELS = {f"workflow:{kind}" for kind in LABELS}
WRITE_PERMISSIONS = {"ADMIN", "MAINTAIN", "WRITE"}
Runner = Callable[[list[str], str | None], str]


class BackendError(RuntimeError):
    """A safe, user-facing backend failure."""


@dataclass(frozen=True)
class Repository:
    name: str
    url: str
    permission: str
    issues_enabled: bool


class GhClient:
    def __init__(
        self,
        repository: str | None = None,
        login: str | None = None,
        runner: Runner | None = None,
    ):
        self.requested_repository = repository
        self.requested_login = login
        self._runner = runner or self._run
        self._repository: Repository | None = None
        self._current_login: str | None = None
        self._accounts: list[dict[str, Any]] | None = None

    @staticmethod
    def _run(arguments: list[str], input_text: str | None = None) -> str:
        try:
            completed = subprocess.run(
                ["gh", *arguments],
                input=input_text,
                text=True,
                capture_output=True,
                check=False,
            )
        except FileNotFoundError as error:
            raise BackendError("gh is not installed or is not on PATH") from error
        if completed.returncode:
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise BackendError(detail or f"gh exited with status {completed.returncode}")
        return completed.stdout

    def repository(self) -> Repository:
        if self._repository is not None:
            return self._repository
        arguments = ["repo", "view"]
        if self.requested_repository:
            arguments.append(self.requested_repository)
        arguments.extend(
            ("--json", "nameWithOwner,url,viewerPermission,hasIssuesEnabled")
        )
        try:
            data = json.loads(self._runner(arguments, None))
        except json.JSONDecodeError as error:
            raise BackendError("gh repo view returned invalid JSON") from error
        self._repository = Repository(
            name=data.get("nameWithOwner", ""),
            url=data.get("url", ""),
            permission=data.get("viewerPermission", ""),
            issues_enabled=data.get("hasIssuesEnabled") is True,
        )
        return self._repository

    def auth_accounts(self) -> list[dict[str, Any]]:
        if self._accounts is None:
            try:
                data = json.loads(
                    self._runner(
                        [
                            "auth",
                            "status",
                            "--hostname",
                            "github.com",
                            "--json",
                            "hosts",
                        ],
                        None,
                    )
                )
            except json.JSONDecodeError as error:
                raise BackendError("gh auth status returned invalid JSON") from error
            accounts = data.get("hosts", {}).get("github.com", [])
            self._accounts = [
                {
                    "active": account.get("active") is True,
                    "login": account.get("login", ""),
                    "state": account.get("state", ""),
                }
                for account in accounts
                if account.get("login")
            ]
        return self._accounts

    def require_login(self) -> str:
        if not self.requested_login:
            raise BackendError("--login is required to select an authenticated GitHub account")
        accounts = self.auth_accounts()
        selected = next(
            (account for account in accounts if account["login"] == self.requested_login),
            None,
        )
        if selected is None:
            raise BackendError(
                f"GitHub account {self.requested_login} is not authenticated on github.com"
            )
        if selected["state"] != "success":
            raise BackendError(
                f"GitHub authentication for {self.requested_login} is not valid"
            )
        if not selected["active"]:
            raise BackendError(
                f"GitHub account {self.requested_login} is not active; run "
                f"gh auth switch --hostname github.com --user {self.requested_login} and retry"
            )
        return self.requested_login

    def preflight(self) -> dict[str, Any]:
        login = self.current_user()
        repository = self.repository()
        errors = []
        if not repository.name or not repository.url.startswith("https://github.com/"):
            errors.append("the GitHub backend requires a github.com repository")
        if not repository.issues_enabled:
            errors.append("GitHub Issues is disabled for the repository")
        if repository.permission not in WRITE_PERMISSIONS:
            errors.append(
                "repository write permission is required for issues, relationships, and labels"
            )
        if errors:
            raise BackendError("; ".join(errors))
        return {
            "capabilities": {
                "issue_dependencies": "native",
                "sub_issues": "native",
            },
            "authenticated_accounts": [account["login"] for account in self.auth_accounts()],
            "issues_enabled": True,
            "login": login,
            "permission": repository.permission,
            "repository": repository.name,
        }

    def api(
        self,
        endpoint: str,
        *,
        method: str = "GET",
        payload: dict[str, Any] | None = None,
        paginate: bool = False,
    ) -> Any:
        arguments = ["api", "--method", method, endpoint]
        if paginate:
            arguments.extend(("--paginate", "--slurp"))
        input_text = None
        if payload is not None:
            arguments.extend(("--input", "-"))
            input_text = json.dumps(payload, separators=(",", ":"))
        output = self._runner(arguments, input_text)
        if not output.strip():
            return None
        try:
            data = json.loads(output)
        except json.JSONDecodeError as error:
            raise BackendError(f"gh api returned invalid JSON for {endpoint}") from error
        if paginate:
            if not isinstance(data, list):
                raise BackendError(f"paginated response is not a list for {endpoint}")
            flattened = []
            for page in data:
                if not isinstance(page, list):
                    raise BackendError(f"paginated response contains a non-list page for {endpoint}")
                flattened.extend(page)
            return flattened
        return data

    def current_user(self) -> str:
        if self._current_login is not None:
            return self._current_login
        login = self.require_login()
        data = self.api("/user")
        actual = data.get("login") if isinstance(data, dict) else None
        if actual != login:
            raise BackendError(
                f"gh api authenticated as {actual or 'unknown'}, expected {login}"
            )
        self._current_login = login
        return login


class GitHubBackend:
    def __init__(self, client: GhClient):
        self.client = client

    @property
    def repository(self) -> str:
        return self.client.repository().name

    def _endpoint(self, suffix: str = "") -> str:
        return f"/repos/{self.repository}{suffix}"

    @staticmethod
    def _label_name(kind: str) -> str:
        if kind not in LABELS:
            raise BackendError(f"unknown workflow kind: {kind}")
        return f"workflow:{kind}"

    @staticmethod
    def _label_names(issue: dict[str, Any]) -> list[str]:
        result = []
        for label in issue.get("labels", []):
            result.append(label if isinstance(label, str) else label.get("name", ""))
        return [name for name in result if name]

    def _issue(self, number: int) -> dict[str, Any]:
        issue = self.client.api(self._endpoint(f"/issues/{number}"))
        if not isinstance(issue, dict) or "pull_request" in issue:
            raise BackendError(f"#{number} is not a repository issue")
        return issue

    def _many(self, suffix: str) -> list[dict[str, Any]]:
        separator = "&" if "?" in suffix else "?"
        result = self.client.api(
            self._endpoint(f"{suffix}{separator}per_page=100"), paginate=True
        )
        if not isinstance(result, list):
            raise BackendError(f"expected a list from {suffix}")
        return result

    def preflight(self) -> dict[str, Any]:
        return self.client.preflight()

    def label_plan(self) -> dict[str, Any]:
        current = {
            label["name"]: {
                "color": label.get("color", "").upper(),
                "description": label.get("description") or "",
            }
            for label in self._many("/labels")
        }
        changes = []
        for kind, settings in LABELS.items():
            name = self._label_name(kind)
            desired = {
                "color": settings["color"].upper(),
                "description": settings["description"],
            }
            existing = current.get(name)
            action = "create" if existing is None else "unchanged" if existing == desired else "update"
            changes.append(
                {
                    "action": action,
                    "desired": desired,
                    "expected": existing,
                    "name": name,
                }
            )
        return {"changes": changes, "repository": self.repository, "schema": 1}

    def apply_label_plan(self, plan: dict[str, Any]) -> dict[str, Any]:
        if plan.get("schema") != 1 or plan.get("repository") != self.repository:
            raise BackendError("label plan does not match this repository")
        current_plan = self.label_plan()
        if current_plan != plan:
            raise BackendError("label state changed after the reviewed plan; generate a new plan")
        applied = []
        for change in plan["changes"]:
            if change["action"] == "unchanged":
                continue
            payload = {"name": change["name"], **change["desired"]}
            if change["action"] == "create":
                self.client.api(self._endpoint("/labels"), method="POST", payload=payload)
            elif change["action"] == "update":
                encoded = quote(change["name"], safe="")
                self.client.api(
                    self._endpoint(f"/labels/{encoded}"), method="PATCH", payload=payload
                )
            else:
                raise BackendError(f"unknown label-plan action: {change['action']}")
            applied.append(change["name"])
        return {"applied": applied, "repository": self.repository}

    def _require_repository_label(self, name: str) -> str:
        encoded = quote(name, safe="")
        try:
            existing = self.client.api(self._endpoint(f"/labels/{encoded}"))
        except BackendError as error:
            raise BackendError(f"required label {name} is unavailable") from error
        if not isinstance(existing, dict) or existing.get("name") != name:
            raise BackendError(f"required label {name} is unavailable")
        return name

    def _require_label(self, kind: str) -> str:
        name = self._label_name(kind)
        try:
            return self._require_repository_label(name)
        except BackendError as error:
            raise BackendError(
                f"required label {name} is unavailable; review and apply a label plan first"
            ) from error

    def _extra_labels(self, labels: list[str]) -> list[str]:
        result = []
        for name in labels:
            if name.startswith("workflow:"):
                raise BackendError("set semantic kind with --kind, not an extra workflow label")
            result.append(self._require_repository_label(name))
        return result

    def create(
        self, title: str, body: str, kind: str, labels: list[str] | None = None
    ) -> dict[str, Any]:
        issue_labels = [self._require_label(kind), *self._extra_labels(labels or [])]
        return self.client.api(
            self._endpoint("/issues"),
            method="POST",
            payload={"body": body, "labels": issue_labels, "title": title},
        )

    def read(self, number: int) -> dict[str, Any]:
        return {
            "blocked_by": self._many(f"/issues/{number}/dependencies/blocked_by"),
            "comments": self._many(f"/issues/{number}/comments"),
            "issue": self._issue(number),
            "sub_issues": self._many(f"/issues/{number}/sub_issues"),
        }

    def list(
        self,
        *,
        state: str = "open",
        kind: str | None = None,
        labels: list[str] | None = None,
        assignee: str | None = None,
        parent: int | None = None,
    ) -> list[dict[str, Any]]:
        if state not in {"open", "closed", "all"}:
            raise BackendError(f"invalid issue state: {state}")
        issues = (
            self._many(f"/issues/{parent}/sub_issues")
            if parent is not None
            else self._many(f"/issues?state={state}")
        )
        issues = [issue for issue in issues if "pull_request" not in issue]
        if parent is not None and state != "all":
            issues = [issue for issue in issues if issue.get("state") == state]
        if kind:
            label = self._label_name(kind)
            issues = [issue for issue in issues if label in self._label_names(issue)]
        for label in labels or []:
            issues = [issue for issue in issues if label in self._label_names(issue)]
        if assignee:
            login = self.client.current_user() if assignee == "@me" else assignee
            issues = [
                issue
                for issue in issues
                if any(item.get("login") == login for item in issue.get("assignees", []))
            ]
        return sorted(issues, key=lambda issue: issue["number"])

    def update(
        self,
        number: int,
        *,
        title: str | None = None,
        body: str | None = None,
        kind: str | None = None,
        add_labels: list[str] | None = None,
        remove_labels: list[str] | None = None,
        state: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if title is not None:
            payload["title"] = title
        if body is not None:
            payload["body"] = body
        add_labels = add_labels or []
        remove_labels = remove_labels or []
        if kind is not None or add_labels or remove_labels:
            issue = self._issue(number)
            labels = self._label_names(issue)
            if kind is not None:
                labels = [name for name in labels if name not in MANAGED_LABELS]
                labels.append(self._require_label(kind))
            for name in self._extra_labels(add_labels):
                if name not in labels:
                    labels.append(name)
            for name in remove_labels:
                if name.startswith("workflow:"):
                    raise BackendError("change semantic kind with --kind; do not remove it")
                labels = [existing for existing in labels if existing != name]
            payload["labels"] = sorted(labels)
        if state is not None:
            if state != "open":
                raise BackendError("use resolve or cancel to close an issue")
            payload.update({"state": "open", "state_reason": "reopened"})
        if not payload:
            raise BackendError("update requires a title, body, kind, label change, or state")
        return self.client.api(
            self._endpoint(f"/issues/{number}"), method="PATCH", payload=payload
        )

    def comment(self, number: int, body: str) -> dict[str, Any]:
        return self.client.api(
            self._endpoint(f"/issues/{number}/comments"),
            method="POST",
            payload={"body": body},
        )

    def claim(self, number: int, assignee: str = "@me") -> dict[str, Any]:
        login = self.client.current_user() if assignee == "@me" else assignee
        issue = self._issue(number)
        if issue.get("state") != "open":
            raise BackendError(f"issue #{number} is not open and cannot be claimed")
        current = sorted(item["login"] for item in issue.get("assignees", []))
        if current == [login]:
            return {"assignee": login, "changed": False, "number": number}
        if current:
            raise BackendError(f"issue #{number} is already claimed by {', '.join(current)}")
        self.client.api(
            self._endpoint(f"/issues/{number}/assignees"),
            method="POST",
            payload={"assignees": [login]},
        )
        return {"assignee": login, "changed": True, "number": number}

    def _close(self, number: int, body: str, reason: str) -> dict[str, Any]:
        if self._issue(number).get("state") != "open":
            raise BackendError(f"issue #{number} is already closed")
        self.comment(number, body)
        issue = self.client.api(
            self._endpoint(f"/issues/{number}"),
            method="PATCH",
            payload={"state": "closed", "state_reason": reason},
        )
        return {"issue": issue, "resolution_comment_added": True}

    def resolve(self, number: int, body: str) -> dict[str, Any]:
        return self._close(number, body, "completed")

    def cancel(self, number: int, body: str) -> dict[str, Any]:
        return self._close(number, body, "not_planned")

    def add_parent(self, parent: int, child: int) -> dict[str, Any]:
        if parent == child:
            raise BackendError("an issue cannot be its own parent")
        child_issue = self._issue(child)
        children = self._many(f"/issues/{parent}/sub_issues")
        if any(item.get("id") == child_issue.get("id") for item in children):
            return {"changed": False, "child": child, "parent": parent}
        self.client.api(
            self._endpoint(f"/issues/{parent}/sub_issues"),
            method="POST",
            payload={"sub_issue_id": child_issue["id"]},
        )
        return {"changed": True, "child": child, "parent": parent}

    def remove_parent(self, parent: int, child: int) -> dict[str, Any]:
        child_issue = self._issue(child)
        children = self._many(f"/issues/{parent}/sub_issues")
        if not any(item.get("id") == child_issue.get("id") for item in children):
            return {"changed": False, "child": child, "parent": parent}
        self.client.api(
            self._endpoint(f"/issues/{parent}/sub_issue"),
            method="DELETE",
            payload={"sub_issue_id": child_issue["id"]},
        )
        return {"changed": True, "child": child, "parent": parent}

    def add_blocker(self, issue_number: int, blocker_number: int) -> dict[str, Any]:
        if issue_number == blocker_number:
            raise BackendError("an issue cannot block itself")
        blocker = self._issue(blocker_number)
        existing = self._many(f"/issues/{issue_number}/dependencies/blocked_by")
        if any(item.get("id") == blocker.get("id") for item in existing):
            return {"blocked": issue_number, "blocker": blocker_number, "changed": False}
        self.client.api(
            self._endpoint(f"/issues/{issue_number}/dependencies/blocked_by"),
            method="POST",
            payload={"issue_id": blocker["id"]},
        )
        return {"blocked": issue_number, "blocker": blocker_number, "changed": True}

    def remove_blocker(self, issue_number: int, blocker_number: int) -> dict[str, Any]:
        blocker = self._issue(blocker_number)
        existing = self._many(f"/issues/{issue_number}/dependencies/blocked_by")
        if not any(item.get("id") == blocker.get("id") for item in existing):
            return {"blocked": issue_number, "blocker": blocker_number, "changed": False}
        self.client.api(
            self._endpoint(
                f"/issues/{issue_number}/dependencies/blocked_by/{blocker['id']}"
            ),
            method="DELETE",
        )
        return {"blocked": issue_number, "blocker": blocker_number, "changed": True}

    def frontier(self, parent: int) -> list[dict[str, Any]]:
        candidates = [
            issue
            for issue in self._many(f"/issues/{parent}/sub_issues")
            if issue.get("state") == "open" and not issue.get("assignees")
        ]
        frontier = []
        for issue in candidates:
            blockers = self._many(
                f"/issues/{issue['number']}/dependencies/blocked_by"
            )
            if all(
                blocker.get("state") == "closed"
                and blocker.get("state_reason") == "completed"
                for blocker in blockers
            ):
                frontier.append(issue)
        return sorted(frontier, key=lambda issue: issue["number"])


def _read_body(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text()


def _write_json(value: Any, output: str | None = None) -> None:
    text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if output:
        Path(output).write_text(text)
    else:
        sys.stdout.write(text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", help="OWNER/REPO; defaults to the current repository")
    parser.add_argument(
        "--login", required=True, help="configured github.com account login"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("preflight")

    plan = commands.add_parser("labels-plan")
    plan.add_argument("--output")
    apply = commands.add_parser("labels-apply")
    apply.add_argument("--plan-file", required=True)
    apply.add_argument("--yes", action="store_true")

    create = commands.add_parser("create")
    create.add_argument("--title", required=True)
    create.add_argument("--body-file", required=True)
    create.add_argument("--kind", choices=sorted(LABELS), required=True)
    create.add_argument("--label", action="append", default=[])

    read = commands.add_parser("read")
    read.add_argument("number", type=int)
    listing = commands.add_parser("list")
    listing.add_argument("--state", choices=("open", "closed", "all"), default="open")
    listing.add_argument("--kind", choices=sorted(LABELS))
    listing.add_argument("--label", action="append", default=[])
    listing.add_argument("--assignee")
    listing.add_argument("--parent", type=int)

    update = commands.add_parser("update")
    update.add_argument("number", type=int)
    update.add_argument("--title")
    update.add_argument("--body-file")
    update.add_argument("--kind", choices=sorted(LABELS))
    update.add_argument("--add-label", action="append", default=[])
    update.add_argument("--remove-label", action="append", default=[])
    update.add_argument("--state", choices=("open",))

    for name in ("comment", "resolve", "cancel"):
        command = commands.add_parser(name)
        command.add_argument("number", type=int)
        command.add_argument("--body-file", required=True)

    claim = commands.add_parser("claim")
    claim.add_argument("number", type=int)
    claim.add_argument("--assignee", default="@me")

    for name in ("parent-add", "parent-remove"):
        command = commands.add_parser(name)
        command.add_argument("parent", type=int)
        command.add_argument("child", type=int)
    for name in ("block-add", "block-remove"):
        command = commands.add_parser(name)
        command.add_argument("issue", type=int)
        command.add_argument("blocker", type=int)
    frontier = commands.add_parser("frontier")
    frontier.add_argument("parent", type=int)
    return parser


def main(arguments: list[str] | None = None) -> int:
    args = build_parser().parse_args(arguments)
    client = GhClient(args.repo, args.login)
    backend = GitHubBackend(client)
    try:
        client.current_user()
        if args.command == "preflight":
            result = backend.preflight()
        elif args.command == "labels-plan":
            result = backend.label_plan()
            _write_json(result, args.output)
            return 0
        elif args.command == "labels-apply":
            if not args.yes:
                raise BackendError("labels-apply requires --yes after reviewing the plan")
            result = backend.apply_label_plan(json.loads(Path(args.plan_file).read_text()))
        elif args.command == "create":
            result = backend.create(
                args.title, _read_body(args.body_file), args.kind, args.label
            )
        elif args.command == "read":
            result = backend.read(args.number)
        elif args.command == "list":
            result = backend.list(
                state=args.state,
                kind=args.kind,
                labels=args.label,
                assignee=args.assignee,
                parent=args.parent,
            )
        elif args.command == "update":
            result = backend.update(
                args.number,
                title=args.title,
                body=_read_body(args.body_file) if args.body_file else None,
                kind=args.kind,
                add_labels=args.add_label,
                remove_labels=args.remove_label,
                state=args.state,
            )
        elif args.command == "comment":
            result = backend.comment(args.number, _read_body(args.body_file))
        elif args.command == "claim":
            result = backend.claim(args.number, args.assignee)
        elif args.command == "resolve":
            result = backend.resolve(args.number, _read_body(args.body_file))
        elif args.command == "cancel":
            result = backend.cancel(args.number, _read_body(args.body_file))
        elif args.command == "parent-add":
            result = backend.add_parent(args.parent, args.child)
        elif args.command == "parent-remove":
            result = backend.remove_parent(args.parent, args.child)
        elif args.command == "block-add":
            result = backend.add_blocker(args.issue, args.blocker)
        elif args.command == "block-remove":
            result = backend.remove_blocker(args.issue, args.blocker)
        elif args.command == "frontier":
            result = backend.frontier(args.parent)
        else:  # pragma: no cover
            raise BackendError(f"unknown command: {args.command}")
    except (BackendError, OSError, json.JSONDecodeError) as error:
        print(f"github issue backend: {error}", file=sys.stderr)
        return 1
    _write_json(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
