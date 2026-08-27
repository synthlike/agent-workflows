#!/usr/bin/env python3
"""Local Markdown reference adapter for the portable semantic record contract."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any, Callable

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows fallback
    fcntl = None
    import msvcrt

from contract import (
    RecordError,
    IssueRecord,
    MigrationRequest,
    MigrationResponse,
    IssueRequest,
    IssueResponse,
    RecordReference,
    RecordRequest,
    RecordResponse,
    StoredRecord,
    canonical_json,
    migration_reference_key,
    revision_token,
)


METADATA = re.compile(
    rb"\A<!-- agent-workflows-record\n(?P<json>\{.*?\})\n-->\n(?P<body>.*)\Z",
    re.S,
)
RECORD_ID = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?")
SUPPORTED_RECORD_TYPES = {
    "arps",
    "domain",
    "handoffs",
    "meetings",
    "problem_framing",
    "prototypes",
    "questionnaires",
    "research",
    "rfcs",
    "specs",
    "technical_baselines",
}
PREFIXED_RECORD_TYPES = {"arps", "rfcs"}
ISSUE_ID = re.compile(r"ISSUE-[0-9]{4,}")
ISSUE_STATUSES = {"open", "claimed", "resolved", "cancelled"}
ISSUE_FRONTMATTER = re.compile(rb"\A---\n(?P<meta>.*?)\n---\n(?P<body>.*)\Z", re.S)


class LocalMarkdownAdapter:
    def __init__(
        self,
        root: Path,
        backend: str,
        clock: Callable[[], str] | None = None,
    ):
        self.root = root.resolve()
        self.backend = backend
        self.clock = clock or (
            lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        )

    @contextmanager
    def _lock(self, scope: Path):
        identity = hashlib.sha256(str(scope.resolve()).encode()).hexdigest()
        lock_path = Path(tempfile.gettempdir()) / f"agent-workflows-{identity}.lock"
        with lock_path.open("a+b") as lock:
            if fcntl is not None:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            else:  # pragma: no cover - Windows fallback
                lock.seek(0)
                lock.write(b"0")
                lock.flush()
                msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                if fcntl is not None:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
                else:  # pragma: no cover - Windows fallback
                    lock.seek(0)
                    msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)

    def render_reference(self, reference: RecordReference) -> str:
        title = reference.title.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")
        if reference.href is None:
            return title
        href = reference.href.replace("<", "%3C").replace(">", "%3E")
        return f"[{title}](<{href}>)"

    def execute(self, request: RecordRequest) -> RecordResponse:
        request.validate()
        if request.backend != self.backend:
            raise RecordError(
                "backend_mismatch",
                f"request targets backend {request.backend}, adapter serves {self.backend}",
            )
        if request.record_type not in SUPPORTED_RECORD_TYPES:
            raise RecordError(
                "unsupported_record_type",
                f"local adapter does not support {request.record_type}",
            )
        destination = self._destination(request.destination, request.record_type)
        if request.operation == "create":
            return RecordResponse(
                record=self._create(
                    request,
                    destination,
                    request.destination.get("prefix"),
                )
            )
        if request.operation == "read":
            return RecordResponse(
                record=self._read_id(request.id or "", destination, request.record_type)
            )
        if request.operation == "list":
            return RecordResponse(records=tuple(self._list(request, destination)))
        if request.operation == "update":
            return RecordResponse(record=self._update(request, destination, archived=False))
        if request.operation == "archive":
            return RecordResponse(record=self._update(request, destination, archived=True))
        raise RecordError("unsupported_operation", request.operation)

    def execute_issue(self, request: IssueRequest) -> IssueResponse:
        request.validate()
        if request.backend != self.backend:
            raise RecordError(
                "backend_mismatch",
                f"request targets backend {request.backend}, adapter serves {self.backend}",
            )
        root = self._issue_root(request.destination)
        if request.operation == "create":
            return IssueResponse(issue=self._create_issue(request, root))
        if request.operation == "read":
            return IssueResponse(issue=self._read_issue(request.id or "", root)[0])
        if request.operation == "list":
            return IssueResponse(issues=tuple(self._list_issues(request, root)))
        if request.operation == "frontier":
            return IssueResponse(issues=tuple(self._frontier(request.id or "", root)))
        if request.operation == "update":
            return IssueResponse(issue=self._mutate_issue(request, root, self._change_issue))
        if request.operation == "comment":
            return IssueResponse(issue=self._mutate_issue(request, root, self._comment_issue))
        if request.operation == "claim":
            return IssueResponse(issue=self._mutate_issue(request, root, self._claim_issue))
        if request.operation == "resolve":
            return IssueResponse(issue=self._mutate_issue(request, root, self._resolve_issue))
        if request.operation == "cancel":
            return IssueResponse(issue=self._mutate_issue(request, root, self._cancel_issue))
        if request.operation == "parent":
            return IssueResponse(issue=self._mutate_issue(request, root, self._parent_issue))
        if request.operation == "block":
            return IssueResponse(issue=self._mutate_issue(request, root, self._block_issue))
        raise RecordError("unsupported_operation", request.operation)

    def execute_migration(self, request: MigrationRequest) -> MigrationResponse:
        request.validate()
        if request.backend != self.backend or request.backend_type != "local-markdown":
            raise RecordError("backend_mismatch", "migration request targets another backend")
        if request.record_type == "issues":
            root = self._issue_root(request.destination)
            if request.operation == "export-history":
                snapshots = tuple(
                    self._issue_snapshot(path, root) for path in self._issue_candidates(root)
                )
                return MigrationResponse(
                    snapshots=tuple(sorted(snapshots, key=self._snapshot_sort_key))
                )
            if request.operation == "import":
                return self._migration_import_issue(request, root)
            if request.operation == "verify":
                return self._migration_verify_issue(request, root)
            return self._migration_retire_issue(request, root)
        if request.record_type not in SUPPORTED_RECORD_TYPES:
            raise RecordError(
                "unsupported_record_type",
                f"local adapter does not support {request.record_type}",
            )
        destination = self._destination(request.destination, request.record_type)
        if request.operation == "export-history":
            snapshots = tuple(self._record_snapshots(request.record_type, destination))
            return MigrationResponse(snapshots=snapshots)
        if request.operation == "import":
            return self._migration_import_record(request, destination)
        if request.operation == "verify":
            return self._migration_verify_record(request, destination)
        return self._migration_retire_record(request, destination)

    @staticmethod
    def _sha256(data: bytes) -> str:
        return "sha256:" + hashlib.sha256(data).hexdigest()

    @staticmethod
    def _snapshot_sort_key(snapshot: dict[str, Any]) -> tuple[str, str, str]:
        return (
            snapshot["identity"]["semantic_id"],
            snapshot["source"]["reference"]["backend"],
            snapshot["source"]["reference"]["id"],
        )

    @staticmethod
    def _modified(path: Path) -> str:
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()

    @staticmethod
    def _migration_metadata(snapshot: dict[str, Any]) -> dict[str, Any]:
        return {
            "content_sha256": snapshot["content_sha256"],
            "created": snapshot["created"],
            "identity": snapshot["identity"],
            "issue": snapshot["issue"],
            "modified": snapshot["modified"],
            "provenance": snapshot["provenance"],
            "source": snapshot["source"],
        }

    @staticmethod
    def _source_key(snapshot: dict[str, Any]) -> str:
        return migration_reference_key(snapshot["source"]["reference"])

    def _validate_snapshot(self, snapshot: dict[str, Any], record_type: str) -> None:
        required = {
            "snapshot_version", "record_type", "source", "identity", "title",
            "content", "content_sha256", "created", "modified", "lifecycle",
            "provenance", "issue",
        }
        if not isinstance(snapshot, dict) or set(snapshot) != required:
            raise RecordError("invalid_request", "migration snapshot fields are invalid")
        if snapshot["snapshot_version"] != 1 or snapshot["record_type"] != record_type:
            raise RecordError("unsupported_record_type", "migration snapshot type is invalid")
        if not isinstance(snapshot["title"], str) or not snapshot["title"]:
            raise RecordError("invalid_request", "migration snapshot title is invalid")
        if not isinstance(snapshot["content"], str) or snapshot["content_sha256"] != self._sha256(
            snapshot["content"].encode()
        ):
            raise RecordError("invalid_request", "migration snapshot content hash is invalid")
        if not isinstance(snapshot["created"], str) or not isinstance(snapshot["modified"], str):
            raise RecordError("invalid_request", "migration snapshot timestamps are invalid")
        source = snapshot["source"]
        identity = snapshot["identity"]
        lifecycle = snapshot["lifecycle"]
        if (
            not isinstance(source, dict)
            or set(source) != {"backend_instance", "backend_type", "reference", "revision"}
            or not isinstance(source["revision"], str)
            or not source["revision"]
            or not isinstance(identity, dict)
            or set(identity) != {"semantic_id", "provider_id"}
            or any(not isinstance(identity[key], str) or not identity[key] for key in identity)
            or not isinstance(lifecycle, dict)
            or set(lifecycle) != {"state", "archived"}
            or type(lifecycle["archived"]) is not bool
            or not isinstance(snapshot["provenance"], list)
        ):
            raise RecordError("invalid_request", "migration snapshot values are invalid")
        try:
            source_reference = RecordReference.from_dict(source["reference"])
        except RecordError as error:
            raise RecordError("invalid_request", "migration source reference is invalid") from error
        if (
            not isinstance(source["backend_instance"], str)
            or source["backend_instance"] != source_reference.backend
            or not isinstance(source["backend_type"], str)
            or not source["backend_type"]
        ):
            raise RecordError("invalid_request", "migration source identity is invalid")
        classifications = {
            "portable-native", "portable-represented", "provider-informational",
            "provider-required", "unsupported",
        }
        provenance = snapshot["provenance"]
        if any(
            not isinstance(value, dict)
            or set(value) != {"classification", "name", "value"}
            or value["classification"] not in classifications
            or not isinstance(value["name"], str)
            or not value["name"]
            for value in provenance
        ) or provenance != sorted(
            provenance,
            key=lambda value: (
                value["classification"], value["name"], canonical_json(value["value"])
            ),
        ):
            raise RecordError("invalid_request", "migration provenance is invalid")
        if any(value["classification"] == "unsupported" for value in provenance):
            raise RecordError("unsupported_fidelity", "migration snapshot contains unsupported values")
        if record_type == "issues":
            issue = snapshot["issue"]
            issue_required = {
                "kind", "status", "assignee", "labels", "comments", "relationships"
            }
            if (
                not isinstance(issue, dict)
                or set(issue) != issue_required
                or not isinstance(issue["kind"], str)
                or not issue["kind"]
                or issue["status"] not in ISSUE_STATUSES
                or issue["assignee"] is not None and not isinstance(issue["assignee"], str)
                or not isinstance(issue["labels"], list)
                or any(not isinstance(label, str) or not label for label in issue["labels"])
                or issue["labels"] != sorted(set(issue["labels"]))
                or not isinstance(issue["comments"], list)
                or not isinstance(issue["relationships"], list)
                or lifecycle["state"] != issue["status"]
                or lifecycle["archived"]
            ):
                raise RecordError("invalid_request", "migration issue state is invalid")
            for comment in issue["comments"]:
                if (
                    not isinstance(comment, dict)
                    or set(comment) != {"id", "author", "created", "body", "reference"}
                    or any(
                        not isinstance(comment[key], str) or not comment[key]
                        for key in ("id", "author", "created")
                    )
                    or not isinstance(comment["body"], str)
                ):
                    raise RecordError("invalid_request", "migration issue comment is invalid")
                if comment["reference"] is not None:
                    try:
                        RecordReference.from_dict(comment["reference"])
                    except RecordError as error:
                        raise RecordError(
                            "invalid_request", "migration comment reference is invalid"
                        ) from error
            for relationship in issue["relationships"]:
                if (
                    not isinstance(relationship, dict)
                    or set(relationship) != {"kind", "target"}
                    or relationship["kind"] not in {"parent", "blocks"}
                ):
                    raise RecordError("invalid_request", "migration relationship is invalid")
                try:
                    RecordReference.from_dict(relationship["target"])
                except RecordError as error:
                    raise RecordError(
                        "invalid_request", "migration relationship target is invalid"
                    ) from error
        elif (
            snapshot["issue"] is not None
            or lifecycle["state"] not in {"active", "archived"}
            or lifecycle["archived"] != (lifecycle["state"] == "archived")
        ):
            raise RecordError("invalid_request", "migration record state is invalid")

    def _record_snapshot(self, record: StoredRecord) -> dict[str, Any]:
        migration = record.metadata.get("migration")
        provenance = [
            {
                "classification": "provider-required",
                "name": "local.path",
                "value": record.reference.id,
            }
        ]
        if migration is not None:
            provenance.append(
                {
                    "classification": "portable-represented",
                    "name": "migration.source",
                    "value": migration,
                }
            )
        if record.metadata.get("legacy"):
            provenance.append(
                {
                    "classification": "provider-informational",
                    "name": "local.legacy_markdown",
                    "value": True,
                }
            )
        return {
            "snapshot_version": 1,
            "record_type": record.record_type,
            "source": {
                "backend_instance": self.backend,
                "backend_type": "local-markdown",
                "reference": record.reference.as_dict(),
                "revision": record.revision,
            },
            "identity": {
                "semantic_id": record.id,
                "provider_id": record.reference.id,
            },
            "title": record.title,
            "content": record.content,
            "content_sha256": self._sha256(record.content.encode()),
            "created": record.metadata["created"],
            "modified": record.metadata["modified"],
            "lifecycle": {
                "state": "archived" if record.metadata["archived"] else "active",
                "archived": record.metadata["archived"],
            },
            "provenance": sorted(
                provenance,
                key=lambda value: (
                    value["classification"], value["name"], canonical_json(value["value"])
                ),
            ),
            "issue": None,
        }

    def _record_snapshots(self, record_type: str, destination: Path) -> list[dict[str, Any]]:
        if not destination.exists():
            return []
        snapshots = []
        for path in sorted(destination.glob("*.md")):
            record = self._deserialize(path, path.read_bytes(), record_type)
            if record.record_type == record_type:
                snapshots.append(self._record_snapshot(record))
        return sorted(snapshots, key=self._snapshot_sort_key)

    @staticmethod
    def _issue_comments(body: str) -> list[dict[str, Any]]:
        comments_marker = "\n## Comments"
        resolution_marker = "\n## Resolution"
        if comments_marker not in body or resolution_marker not in body:
            return []
        section = body.split(comments_marker, 1)[1].split(resolution_marker, 1)[0]
        pattern = re.compile(
            r"(?m)^### (?P<created>.+?) — (?P<author>.+?)\n\n(?P<body>.*?)(?=\n### |\Z)",
            re.S,
        )
        comments = []
        for index, match in enumerate(pattern.finditer(section), 1):
            created = match.group("created").strip()
            author = match.group("author").strip()
            content = match.group("body").strip()
            comments.append(
                {
                    "id": f"comment-{index:04d}",
                    "author": author,
                    "created": created,
                    "body": content,
                    "reference": None,
                }
            )
        return sorted(comments, key=lambda value: (value["created"], value["id"]))

    def _issue_snapshot(self, path: Path, root: Path) -> dict[str, Any]:
        data = path.read_bytes()
        issue = self._issue_from_bytes(path, data, root)
        metadata, _body = self._parse_issue_frontmatter(data, path)
        relationships = []
        if issue.parent:
            relationships.append(
                {
                    "kind": "parent",
                    "target": self._read_issue(issue.parent, root)[0].reference.as_dict(),
                }
            )
        relationships.extend(
            {
                "kind": "blocks",
                "target": self._read_issue(blocker, root)[0].reference.as_dict(),
            }
            for blocker in issue.blocked_by
        )
        relationships.sort(
            key=lambda value: (
                value["kind"], value["target"]["backend"], value["target"]["id"]
            )
        )
        provenance = [
            {
                "classification": "provider-required",
                "name": "local.path",
                "value": issue.reference.id,
            }
        ]
        if "migration" in metadata:
            provenance.append(
                {
                    "classification": "portable-represented",
                    "name": "migration.source",
                    "value": metadata["migration"],
                }
            )
        return {
            "snapshot_version": 1,
            "record_type": "issues",
            "source": {
                "backend_instance": self.backend,
                "backend_type": "local-markdown",
                "reference": issue.reference.as_dict(),
                "revision": issue.revision,
            },
            "identity": {
                "semantic_id": issue.id,
                "provider_id": issue.reference.id,
            },
            "title": issue.title,
            "content": issue.body,
            "content_sha256": self._sha256(issue.body.encode()),
            "created": issue.created,
            "modified": self._modified(path),
            "lifecycle": {"state": issue.status, "archived": False},
            "provenance": sorted(
                provenance,
                key=lambda value: (
                    value["classification"], value["name"], canonical_json(value["value"])
                ),
            ),
            "issue": {
                "kind": issue.kind,
                "status": issue.status,
                "assignee": issue.assignee,
                "labels": sorted(issue.labels),
                "comments": self._issue_comments(issue.body),
                "relationships": relationships,
            },
        }

    def _issue_by_reference(self, reference: RecordReference, root: Path) -> tuple[IssueRecord, Path]:
        for path in self._issue_candidates(root):
            issue = self._issue_from_bytes(path, path.read_bytes(), root)
            if issue.reference.id == reference.id:
                return issue, path
        raise RecordError("not_found", f"destination issue does not exist: {reference.id}")

    def _mapped_issue_id(
        self,
        source_reference: dict[str, Any],
        reference_map: dict[str, RecordReference],
        root: Path,
    ) -> str:
        mapped = reference_map.get(migration_reference_key(source_reference))
        if mapped is None:
            raise RecordError("broken_reference", "migration relationship has no destination mapping")
        return self._issue_by_reference(mapped, root)[0].id

    def _migration_import_record(
        self, request: MigrationRequest, destination: Path
    ) -> MigrationResponse:
        snapshot = request.snapshot or {}
        self._validate_snapshot(snapshot, request.record_type)
        record_id = self._validate_id(snapshot["identity"]["semantic_id"])
        with self._lock(destination):
            try:
                existing = self._read_id(record_id, destination, request.record_type)
            except RecordError as error:
                if error.code != "not_found":
                    raise
            else:
                migration = existing.metadata.get("migration", {})
                if migration.get("source") != snapshot["source"]:
                    raise RecordError("duplicate_id", f"record id already exists: {record_id}")
                return self._migration_verify_record(
                    replace(request, operation="verify", destination_reference=existing.reference),
                    destination,
                )
            destination.mkdir(parents=True, exist_ok=True)
            path = self._path(destination, record_id)
            metadata = {
                "archived": snapshot["lifecycle"]["archived"],
                "created": snapshot["created"],
                "id": record_id,
                "migration": self._migration_metadata(snapshot),
                "modified": snapshot["modified"],
                "record_type": request.record_type,
                "title": snapshot["title"],
            }
            data = self._serialize(metadata, snapshot["content"])
            try:
                with path.open("xb") as output:
                    output.write(data)
                    output.flush()
                    os.fsync(output.fileno())
            except FileExistsError as error:
                raise RecordError("duplicate_id", f"record id already exists: {record_id}") from error
            imported = self._deserialize(path, data, request.record_type)
            return MigrationResponse(
                snapshot=self._record_snapshot(imported),
                reference=imported.reference,
                revision=imported.revision,
                verified=True,
            )

    def _migration_import_issue(
        self, request: MigrationRequest, root: Path
    ) -> MigrationResponse:
        snapshot = request.snapshot or {}
        self._validate_snapshot(snapshot, "issues")
        body = snapshot["content"]
        if (
            body != body.rstrip() + "\n"
            or not body.startswith(f"# {snapshot['title']}")
            or "\n## Comments" not in body
            or "\n## Resolution" not in body
        ):
            raise RecordError(
                "invalid_state",
                "source issue content cannot be represented byte-for-byte in local Markdown",
            )
        source_key = self._source_key(snapshot)
        with self._lock(root):
            for path in self._issue_candidates(root):
                metadata, _existing_body = self._parse_issue_frontmatter(path.read_bytes(), path)
                migration = metadata.get("migration", {})
                if migration_reference_key(migration.get("source", {}).get("reference", {})) == source_key:
                    issue = self._issue_from_bytes(path, path.read_bytes(), root)
                    return self._migration_verify_issue(
                        replace(request, operation="verify", destination_reference=issue.reference),
                        root,
                    )
            preferred = snapshot["identity"]["semantic_id"]
            issue_id = preferred if ISSUE_ID.fullmatch(preferred) else ""
            if issue_id:
                try:
                    self._read_issue(issue_id, root)
                except RecordError as error:
                    if error.code != "not_found":
                        raise
                else:
                    raise RecordError("duplicate_id", f"issue id already exists: {issue_id}")
            issue_dir = root / "issues"
            issue_dir.mkdir(parents=True, exist_ok=True)
            if not issue_id:
                numbers = [
                    int(match.group(1))
                    for path in self._issue_candidates(root)
                    if (match := re.search(r"ISSUE-([0-9]+)", path.name))
                ]
                issue_id = f"ISSUE-{max(numbers, default=0) + 1:04d}"
            parent = None
            blockers = []
            for relationship in snapshot["issue"]["relationships"]:
                mapped = self._mapped_issue_id(
                    relationship["target"], request.reference_map, root
                )
                if relationship["kind"] == "parent":
                    if parent is not None:
                        raise RecordError("invalid_relationship", "issue has several parents")
                    parent = mapped
                elif relationship["kind"] == "blocks":
                    blockers.append(mapped)
                else:
                    raise RecordError("invalid_relationship", "migration relationship kind is invalid")
            path = issue_dir / f"{issue_id}-{self._slug(snapshot['title'])}.md"
            issue = IssueRecord(
                id=issue_id,
                title=snapshot["title"],
                body=body,
                kind=snapshot["issue"]["kind"],
                status=snapshot["issue"]["status"],
                created=snapshot["created"],
                assignee=snapshot["issue"]["assignee"],
                parent=parent,
                blocked_by=tuple(sorted(blockers)),
                labels=tuple(sorted(snapshot["issue"]["labels"])),
                revision="",
                reference=RecordReference(self.backend, "", snapshot["title"], None),
            )
            data = self._serialize_issue(
                issue, path, root, self._migration_metadata(snapshot)
            )
            try:
                with path.open("xb") as output:
                    output.write(data)
                    output.flush()
                    os.fsync(output.fileno())
            except FileExistsError as error:
                raise RecordError("duplicate_id", f"issue path already exists: {path.name}") from error
            imported = self._issue_from_bytes(path, data, root)
            return MigrationResponse(
                snapshot=self._issue_snapshot(path, root),
                reference=imported.reference,
                revision=imported.revision,
                verified=True,
            )

    def _migration_verify_record(
        self, request: MigrationRequest, destination: Path
    ) -> MigrationResponse:
        snapshot = request.snapshot or {}
        self._validate_snapshot(snapshot, request.record_type)
        reference = request.destination_reference
        assert reference is not None
        path = (self.root / reference.id).resolve()
        try:
            path.relative_to(destination)
        except ValueError as error:
            raise RecordError("invalid_destination", "migration record reference escapes destination") from error
        if not path.is_file():
            raise RecordError("not_found", "migration destination record is missing")
        record = self._deserialize(path, path.read_bytes(), request.record_type)
        migration = record.metadata.get("migration")
        expected = (
            record.id == snapshot["identity"]["semantic_id"]
            and record.title == snapshot["title"]
            and record.content == snapshot["content"]
            and record.metadata["archived"] == snapshot["lifecycle"]["archived"]
            and record.metadata["created"] == snapshot["created"]
            and record.metadata["modified"] == snapshot["modified"]
            and migration == self._migration_metadata(snapshot)
        )
        if not expected:
            raise RecordError("invalid_state", "migration destination is not semantically equal")
        return MigrationResponse(
            snapshot=self._record_snapshot(record),
            reference=record.reference,
            revision=record.revision,
            verified=True,
        )

    def _migration_verify_issue(
        self, request: MigrationRequest, root: Path
    ) -> MigrationResponse:
        snapshot = request.snapshot or {}
        self._validate_snapshot(snapshot, "issues")
        reference = request.destination_reference
        assert reference is not None
        issue, path = self._issue_by_reference(reference, root)
        metadata, _body = self._parse_issue_frontmatter(path.read_bytes(), path)
        migration = metadata.get("migration")
        expected_parent = None
        expected_blockers = []
        for relationship in snapshot["issue"]["relationships"]:
            mapped = self._mapped_issue_id(relationship["target"], request.reference_map, root)
            if relationship["kind"] == "parent":
                expected_parent = mapped
            elif relationship["kind"] == "blocks":
                expected_blockers.append(mapped)
        if not (
            issue.title == snapshot["title"]
            and issue.body == snapshot["content"]
            and issue.created == snapshot["created"]
            and issue.kind == snapshot["issue"]["kind"]
            and issue.status == snapshot["issue"]["status"]
            and issue.assignee == snapshot["issue"]["assignee"]
            and sorted(issue.labels) == sorted(snapshot["issue"]["labels"])
            and issue.parent == expected_parent
            and sorted(issue.blocked_by) == sorted(expected_blockers)
            and migration == self._migration_metadata(snapshot)
        ):
            raise RecordError("invalid_state", "migration destination issue is not semantically equal")
        return MigrationResponse(
            snapshot=self._issue_snapshot(path, root),
            reference=issue.reference,
            revision=issue.revision,
            verified=True,
        )

    def _migration_retire_record(
        self, request: MigrationRequest, destination: Path
    ) -> MigrationResponse:
        with self._lock(destination):
            return self._migration_retire_record_locked(request, destination)

    def _migration_retire_record_locked(
        self, request: MigrationRequest, destination: Path
    ) -> MigrationResponse:
        snapshot = request.snapshot or {}
        self._validate_snapshot(snapshot, request.record_type)
        current = self._read_id(
            snapshot["identity"]["semantic_id"], destination, request.record_type
        )
        if current.metadata["archived"]:
            migration = current.metadata.get("migration", {})
            replay = (
                migration.get("retired_to") == request.destination_reference.as_dict()
                and migration.get("source_revision") == snapshot["source"]["revision"]
            )
            if not replay and current.revision != snapshot["source"]["revision"]:
                raise RecordError("stale_revision", f"record changed since export: {current.id}")
            return MigrationResponse(
                snapshot=self._record_snapshot(current),
                reference=current.reference,
                revision=current.revision,
                verified=True,
            )
        if current.revision != snapshot["source"]["revision"]:
            raise RecordError("stale_revision", f"record changed since export: {current.id}")
        path = self.root / current.reference.id
        metadata = {
            "archived": True,
            "created": current.metadata["created"],
            "id": current.id,
            "migration": {
                **(
                    {"prior": current.metadata["migration"]}
                    if "migration" in current.metadata
                    else {}
                ),
                "retired_to": request.destination_reference.as_dict(),
                "source_revision": current.revision,
            },
            "modified": self.clock(),
            "record_type": current.record_type,
            "title": current.title,
        }
        data = self._serialize(metadata, current.content)
        with tempfile.NamedTemporaryFile(dir=destination, delete=False) as output:
            temporary = Path(output.name)
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        try:
            if revision_token(path.read_bytes()) != current.revision:
                raise RecordError("stale_revision", f"record changed since export: {current.id}")
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
        retired = self._deserialize(path, data, request.record_type)
        return MigrationResponse(
            snapshot=self._record_snapshot(retired),
            reference=retired.reference,
            revision=retired.revision,
            verified=True,
        )

    def _migration_retire_issue(
        self, request: MigrationRequest, root: Path
    ) -> MigrationResponse:
        snapshot = request.snapshot or {}
        self._validate_snapshot(snapshot, "issues")
        issue, path = self._read_issue(snapshot["identity"]["semantic_id"], root)
        rendered = self.render_reference(request.destination_reference)
        marker = f"Migrated to {rendered}. Destination is authoritative."
        if marker in issue.body:
            metadata, _body = self._parse_issue_frontmatter(path.read_bytes(), path)
            migration = metadata.get("migration", {})
            if (
                migration.get("retired_to") != request.destination_reference.as_dict()
                or migration.get("source_revision") != snapshot["source"]["revision"]
            ):
                raise RecordError("invalid_state", "issue has a conflicting migration tombstone")
            return MigrationResponse(
                snapshot=self._issue_snapshot(path, root),
                reference=issue.reference,
                revision=issue.revision,
                verified=True,
            )
        if issue.revision != snapshot["source"]["revision"]:
            raise RecordError("stale_revision", f"issue changed since export: {issue.id}")
        source_metadata, _body = self._parse_issue_frontmatter(path.read_bytes(), path)
        if issue.status in {"open", "claimed"}:
            changed = self._cancel_issue(
                issue,
                IssueRequest(
                    operation="cancel", backend=self.backend,
                    destination=request.destination, id=issue.id,
                    expected_revision=issue.revision, body=marker,
                ),
                root,
            )
        else:
            changed = self._comment_issue(
                issue,
                IssueRequest(
                    operation="comment", backend=self.backend,
                    destination=request.destination, id=issue.id,
                    expected_revision=issue.revision, body=marker,
                    assignee="migration",
                ),
                root,
            )
        retired = self._write_issue(
            IssueRequest(
                operation="update", backend=self.backend,
                destination=request.destination, id=issue.id,
                expected_revision=issue.revision, body=changed.body,
            ),
            root,
            changed,
            path,
            {
                **(
                    {"prior": source_metadata["migration"]}
                    if "migration" in source_metadata
                    else {}
                ),
                "retired_to": request.destination_reference.as_dict(),
                "source_revision": snapshot["source"]["revision"],
            },
        )
        return MigrationResponse(
            snapshot=self._issue_snapshot(path, root),
            reference=retired.reference,
            revision=retired.revision,
            verified=True,
        )

    def _issue_root(self, settings: dict[str, Any]) -> Path:
        if set(settings) != {"root"} or not isinstance(settings.get("root"), str):
            raise RecordError(
                "invalid_destination",
                "local issues destination must contain only a string root",
            )
        value = settings["root"]
        path = Path(value)
        if not value or path.is_absolute():
            raise RecordError("invalid_destination", "local issue root must be consumer-root-relative")
        issue_root = (self.root / path).resolve()
        try:
            issue_root.relative_to(self.root)
        except ValueError as error:
            raise RecordError("invalid_destination", "local issue root escapes the consumer root") from error
        return issue_root

    @staticmethod
    def _parse_scalar(value: str) -> Any:
        value = value.strip()
        if not value:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            if value.startswith("[") and value.endswith("]"):
                return [item.strip() for item in value[1:-1].split(",") if item.strip()]
            return value

    def _parse_issue_frontmatter(self, data: bytes, path: Path) -> tuple[dict[str, Any], str]:
        match = ISSUE_FRONTMATTER.match(data)
        if not match:
            raise RecordError("malformed_record", f"issue frontmatter is malformed: {path}")
        try:
            lines = match.group("meta").decode().splitlines()
            body = match.group("body").decode().lstrip("\n")
        except UnicodeDecodeError as error:
            raise RecordError("malformed_record", f"issue is not UTF-8: {path}") from error
        metadata: dict[str, Any] = {}
        active_list: str | None = None
        for line in lines:
            if line.startswith("  - ") and active_list:
                metadata[active_list].append(self._parse_scalar(line[4:]))
                continue
            if ":" not in line:
                raise RecordError("malformed_record", f"issue frontmatter is invalid: {path}")
            key, value = line.split(":", 1)
            if not key or key in metadata:
                raise RecordError("malformed_record", f"issue frontmatter keys are invalid: {path}")
            parsed = self._parse_scalar(value)
            if parsed is None and key in {"blocked_by", "labels"}:
                parsed = []
                active_list = key
            else:
                active_list = None
            metadata[key] = parsed
        required = {
            "assignee",
            "blocked_by",
            "created",
            "id",
            "kind",
            "labels",
            "parent",
            "status",
            "title",
        }
        if not required.issubset(metadata) or set(metadata) - (required | {"migration"}):
            raise RecordError("malformed_record", f"issue frontmatter fields are invalid: {path}")
        if "migration" in metadata and not isinstance(metadata["migration"], dict):
            raise RecordError("malformed_record", f"issue migration provenance is invalid: {path}")
        if (
            not isinstance(metadata["id"], str)
            or not ISSUE_ID.fullmatch(metadata["id"])
            or not isinstance(metadata["title"], str)
            or not isinstance(metadata["kind"], str)
            or not isinstance(metadata["status"], str)
            or metadata["status"] not in ISSUE_STATUSES
            or not isinstance(metadata["created"], str)
            or metadata["assignee"] is not None
            and not isinstance(metadata["assignee"], str)
            or metadata["parent"] is not None
            and not isinstance(metadata["parent"], str)
            or not isinstance(metadata["blocked_by"], list)
            or not all(isinstance(item, str) for item in metadata["blocked_by"])
            or not isinstance(metadata["labels"], list)
            or not all(isinstance(item, str) for item in metadata["labels"])
        ):
            raise RecordError("malformed_record", f"issue frontmatter values are invalid: {path}")
        return metadata, body

    def _relationship_id(self, source: Path, value: str, root: Path) -> str:
        if ISSUE_ID.fullmatch(value):
            return value
        target = (source.parent / value).resolve()
        try:
            target.relative_to(self.root)
        except ValueError as error:
            raise RecordError("broken_reference", f"relationship escapes consumer root: {value}") from error
        if not target.is_file():
            raise RecordError("broken_reference", f"relationship target does not exist: {value}")
        try:
            metadata, _body = self._parse_issue_frontmatter(target.read_bytes(), target)
        except RecordError:
            return value
        return metadata["id"]

    def _issue_from_bytes(self, path: Path, data: bytes, root: Path) -> IssueRecord:
        metadata, body = self._parse_issue_frontmatter(data, path)
        if not body.startswith(f"# {metadata['title']}"):
            raise RecordError("malformed_record", f"issue heading does not match title: {path}")
        relative = path.relative_to(self.root).as_posix()
        blockers = tuple(
            self._relationship_id(path, item, root) for item in metadata["blocked_by"]
        )
        if any(not ISSUE_ID.fullmatch(item) for item in blockers):
            raise RecordError("broken_reference", f"blocker is not an issue: {path}")
        return IssueRecord(
            id=metadata["id"],
            title=metadata["title"],
            body=body,
            kind=metadata["kind"],
            status=metadata["status"],
            created=metadata["created"],
            assignee=metadata["assignee"],
            parent=(
                self._relationship_id(path, metadata["parent"], root)
                if metadata["parent"]
                else None
            ),
            blocked_by=blockers,
            labels=tuple(metadata["labels"]),
            revision=revision_token(data),
            reference=RecordReference(self.backend, relative, metadata["title"], relative),
        )

    def _issue_candidates(self, root: Path) -> list[Path]:
        if not root.exists():
            return []
        return sorted(
            path
            for path in root.rglob("*.md")
            if path.is_file() and (path.parent.name == "issues" or path.parent == root)
        )

    def _read_issue(self, issue_id: str, root: Path) -> tuple[IssueRecord, Path]:
        if not ISSUE_ID.fullmatch(issue_id):
            raise RecordError("invalid_id", f"invalid issue id: {issue_id}")
        matches = []
        for path in self._issue_candidates(root):
            try:
                metadata, _body = self._parse_issue_frontmatter(path.read_bytes(), path)
            except RecordError:
                if path.parent.name == "issues":
                    raise
                continue
            if metadata["id"] == issue_id:
                matches.append(path)
        if not matches:
            raise RecordError("not_found", f"issue does not exist: {issue_id}")
        if len(matches) > 1:
            raise RecordError("duplicate_id", f"issue id has several owners: {issue_id}")
        path = matches[0]
        return self._issue_from_bytes(path, path.read_bytes(), root), path

    @staticmethod
    def _ensure_issue_body(title: str, body: str) -> str:
        text = body.strip()
        if not text.startswith("# "):
            text = f"# {title}\n\n{text}" if text else f"# {title}"
        else:
            text = re.sub(r"\A# .*", f"# {title}", text, count=1)
        if "\n## Comments" not in text:
            text += "\n\n## Comments\n"
        if "\n## Resolution" not in text:
            text += "\n\n## Resolution\n"
        return text.rstrip() + "\n"

    def _issue_link(self, source: Path, value: str | None, root: Path) -> str | None:
        if value is None or not ISSUE_ID.fullmatch(value):
            return value
        _issue, target = self._read_issue(value, root)
        return Path(os.path.relpath(target, source.parent)).as_posix()

    def _serialize_issue(
        self,
        issue: IssueRecord,
        path: Path,
        root: Path,
        migration: dict[str, Any] | None = None,
    ) -> bytes:
        parent = self._issue_link(path, issue.parent, root)
        blockers = [self._issue_link(path, value, root) for value in issue.blocked_by]
        lines = [
            "---",
            f"id: {issue.id}",
            f"title: {json.dumps(issue.title)}",
            f"kind: {json.dumps(issue.kind)}",
            f"status: {issue.status}",
            f"created: {issue.created}",
            f"assignee: {json.dumps(issue.assignee) if issue.assignee else ''}",
            f"parent: {json.dumps(parent) if parent else ''}",
            "blocked_by:",
        ]
        lines.extend(f"  - {json.dumps(value)}" for value in blockers)
        lines.append("labels: " + json.dumps(list(issue.labels), separators=(",", ":")))
        if migration is not None:
            lines.append(
                "migration: "
                + json.dumps(migration, separators=(",", ":"), sort_keys=True)
            )
        lines.extend(("---", issue.body.rstrip(), ""))
        return "\n".join(lines).encode()

    def _create_issue(self, request: IssueRequest, root: Path) -> IssueRecord:
        with self._lock(root):
            return self._create_issue_locked(request, root)

    def _create_issue_locked(self, request: IssueRequest, root: Path) -> IssueRecord:
        issue_dir = root / "issues"
        issue_dir.mkdir(parents=True, exist_ok=True)
        numbers = []
        for path in self._issue_candidates(root):
            match = re.search(r"ISSUE-([0-9]+)", path.name)
            if match:
                numbers.append(int(match.group(1)))
        number = max(numbers, default=0) + 1
        slug = self._slug(request.title or "issue")
        while True:
            issue_id = f"ISSUE-{number:04d}"
            path = issue_dir / f"{issue_id}-{slug}.md"
            issue = IssueRecord(
                id=issue_id,
                title=request.title or "",
                body=self._ensure_issue_body(request.title or "", request.body or ""),
                kind=request.kind or "task",
                status="open",
                created=self.clock()[:10],
                assignee=None,
                parent=None,
                blocked_by=(),
                labels=tuple(request.labels or ()),
                revision="",
                reference=RecordReference(self.backend, "", request.title or "", None),
            )
            data = self._serialize_issue(issue, path, root)
            try:
                with path.open("xb") as output:
                    output.write(data)
                    output.flush()
                    os.fsync(output.fileno())
                return self._issue_from_bytes(path, data, root)
            except FileExistsError:
                number += 1

    def _list_issues(self, request: IssueRequest, root: Path) -> list[IssueRecord]:
        result = []
        query = (request.query or "").casefold()
        for path in self._issue_candidates(root):
            issue = self._issue_from_bytes(path, path.read_bytes(), root)
            if request.state and request.state != "all" and issue.status != request.state:
                continue
            if request.kind and issue.kind != request.kind:
                continue
            if request.assignee and issue.assignee != request.assignee:
                continue
            if request.parent_id and issue.parent != request.parent_id:
                continue
            if request.labels is not None and not set(request.labels).issubset(issue.labels):
                continue
            if query and query not in f"{issue.id}\n{issue.title}\n{issue.body}".casefold():
                continue
            result.append(issue)
        return sorted(result, key=lambda issue: issue.id)

    def _write_issue(
        self,
        request: IssueRequest,
        root: Path,
        issue: IssueRecord,
        path: Path,
        migration: dict[str, Any] | None = None,
    ) -> IssueRecord:
        with self._lock(root):
            before = path.read_bytes()
            if revision_token(before) != request.expected_revision:
                raise RecordError("stale_revision", f"issue changed since read: {issue.id}")
            metadata, _body = self._parse_issue_frontmatter(before, path)
            data = self._serialize_issue(
                issue,
                path,
                root,
                migration if migration is not None else metadata.get("migration"),
            )
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as output:
                temporary = Path(output.name)
                output.write(data)
                output.flush()
                os.fsync(output.fileno())
            try:
                if revision_token(path.read_bytes()) != request.expected_revision:
                    raise RecordError("stale_revision", f"issue changed since read: {issue.id}")
                os.replace(temporary, path)
            finally:
                temporary.unlink(missing_ok=True)
            return self._issue_from_bytes(path, data, root)

    def _mutate_issue(
        self,
        request: IssueRequest,
        root: Path,
        change: Callable[[IssueRecord, IssueRequest, Path], IssueRecord],
    ) -> IssueRecord:
        current, path = self._read_issue(request.id or "", root)
        if current.revision != request.expected_revision:
            raise RecordError("stale_revision", f"issue changed since read: {current.id}")
        changed = change(current, request, root)
        return self._write_issue(request, root, changed, path)

    def _change_issue(self, issue: IssueRecord, request: IssueRequest, _root: Path) -> IssueRecord:
        title = request.title if request.title is not None else issue.title
        body = request.body if request.body is not None else issue.body
        return replace(
            issue,
            title=title,
            body=self._ensure_issue_body(title, body),
            kind=request.kind if request.kind is not None else issue.kind,
            labels=request.labels if request.labels is not None else issue.labels,
        )

    def _comment_issue(self, issue: IssueRecord, request: IssueRequest, _root: Path) -> IssueRecord:
        marker = "\n## Resolution"
        if marker not in issue.body:
            raise RecordError("malformed_record", f"issue has no resolution section: {issue.id}")
        before, after = issue.body.split(marker, 1)
        author = request.assignee or "agent"
        comment = f"\n\n### {self.clock()} — {author}\n\n{(request.body or '').strip()}\n"
        return replace(issue, body=before.rstrip() + comment + marker + after)

    @staticmethod
    def _claim_issue(issue: IssueRecord, request: IssueRequest, _root: Path) -> IssueRecord:
        if issue.status != "open" or issue.assignee:
            raise RecordError("claim_conflict", f"issue is not unclaimed and open: {issue.id}")
        return replace(issue, status="claimed", assignee=request.assignee)

    @staticmethod
    def _outcome_body(issue: IssueRecord, outcome: str) -> str:
        marker = "\n## Resolution"
        if marker not in issue.body:
            raise RecordError("malformed_record", f"issue has no resolution section: {issue.id}")
        before, _after = issue.body.split(marker, 1)
        return before.rstrip() + marker + "\n\n" + outcome.strip() + "\n"

    def _resolve_issue(self, issue: IssueRecord, request: IssueRequest, _root: Path) -> IssueRecord:
        if issue.status not in {"open", "claimed"}:
            raise RecordError("invalid_state", f"issue cannot be resolved from {issue.status}")
        return replace(issue, status="resolved", body=self._outcome_body(issue, request.body or ""))

    def _cancel_issue(self, issue: IssueRecord, request: IssueRequest, _root: Path) -> IssueRecord:
        if issue.status not in {"open", "claimed"}:
            raise RecordError("invalid_state", f"issue cannot be cancelled from {issue.status}")
        return replace(issue, status="cancelled", body=self._outcome_body(issue, request.body or ""))

    def _parent_issue(self, issue: IssueRecord, request: IssueRequest, root: Path) -> IssueRecord:
        parent = None if request.remove else request.parent_id
        if parent == issue.id:
            raise RecordError("invalid_relationship", "an issue cannot be its own parent")
        seen = {issue.id}
        current = parent
        while current and ISSUE_ID.fullmatch(current):
            if current in seen:
                raise RecordError("invalid_relationship", "parent relationship would create a cycle")
            seen.add(current)
            current = self._read_issue(current, root)[0].parent
        return replace(issue, parent=parent)

    def _depends_on(self, issue_id: str, target: str, root: Path, seen: set[str]) -> bool:
        if issue_id == target:
            return True
        if issue_id in seen:
            return False
        seen.add(issue_id)
        issue = self._read_issue(issue_id, root)[0]
        return any(self._depends_on(blocker, target, root, seen) for blocker in issue.blocked_by)

    def _block_issue(self, issue: IssueRecord, request: IssueRequest, root: Path) -> IssueRecord:
        blocker = request.blocker_id or ""
        if blocker == issue.id:
            raise RecordError("invalid_relationship", "an issue cannot block itself")
        self._read_issue(blocker, root)
        if not request.remove and self._depends_on(blocker, issue.id, root, set()):
            raise RecordError("invalid_relationship", "block relationship would create a cycle")
        blockers = list(issue.blocked_by)
        if request.remove:
            blockers = [value for value in blockers if value != blocker]
        elif blocker not in blockers:
            blockers.append(blocker)
        return replace(issue, blocked_by=tuple(sorted(blockers)))

    def _frontier(self, parent_id: str, root: Path) -> list[IssueRecord]:
        self._read_issue(parent_id, root)
        request = IssueRequest(
            operation="list",
            backend=self.backend,
            destination={"root": str(root.relative_to(self.root))},
            parent_id=parent_id,
        )
        candidates = self._list_issues(request, root)
        frontier = []
        for issue in candidates:
            if issue.status != "open" or issue.assignee:
                continue
            if all(self._read_issue(blocker, root)[0].status == "resolved" for blocker in issue.blocked_by):
                frontier.append(issue)
        return frontier

    def _destination(self, settings: dict[str, Any], record_type: str) -> Path:
        expected = {"path", "prefix"} if record_type in PREFIXED_RECORD_TYPES else {"path"}
        if set(settings) != expected or not isinstance(settings.get("path"), str):
            raise RecordError(
                "invalid_destination",
                f"local {record_type} destination fields must be {', '.join(sorted(expected))}",
            )
        if record_type in PREFIXED_RECORD_TYPES and (
            not isinstance(settings.get("prefix"), str)
            or not re.fullmatch(r"[A-Z][A-Z0-9]*", settings["prefix"])
        ):
            raise RecordError(
                "invalid_destination",
                f"local {record_type} destination requires an uppercase prefix",
            )
        value = settings["path"]
        path = Path(value)
        if not value or path.is_absolute():
            raise RecordError("invalid_destination", "local destination must be consumer-root-relative")
        destination = (self.root / path).resolve()
        try:
            destination.relative_to(self.root)
        except ValueError as error:
            raise RecordError("invalid_destination", "local destination escapes the consumer root") from error
        return destination

    @staticmethod
    def _slug(title: str) -> str:
        value = re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-")
        return value or "research"

    @staticmethod
    def _validate_id(value: str) -> str:
        if not RECORD_ID.fullmatch(value) or value in {".", ".."}:
            raise RecordError("invalid_id", f"invalid local record id: {value}")
        return value

    def _path(self, destination: Path, record_id: str) -> Path:
        return destination / f"{self._validate_id(record_id)}.md"

    @staticmethod
    def _serialize(metadata: dict[str, Any], content: str) -> bytes:
        header = json.dumps(metadata, separators=(",", ":"), sort_keys=True)
        return f"<!-- agent-workflows-record\n{header}\n-->\n{content}".encode()

    def _deserialize(
        self,
        path: Path,
        data: bytes,
        expected_type: str | None = None,
    ) -> StoredRecord:
        match = METADATA.match(data)
        if not match:
            if expected_type not in SUPPORTED_RECORD_TYPES:
                raise RecordError("malformed_record", f"record metadata is malformed: {path}")
            try:
                content = data.decode()
            except UnicodeDecodeError as error:
                raise RecordError("malformed_record", f"record is not UTF-8: {path}") from error
            heading = re.search(r"(?m)^#\s+(.+?)\s*$", content)
            if not heading:
                raise RecordError("malformed_record", f"record has no title heading: {path}")
            record_id = path.stem
            if expected_type in PREFIXED_RECORD_TYPES:
                prefix = re.match(r"([A-Z][A-Z0-9]*-[0-9]+)", record_id)
                if not prefix:
                    raise RecordError("malformed_record", f"prefixed record id is invalid: {path}")
                record_id = prefix.group(1)
            modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
            relative = path.relative_to(self.root).as_posix()
            return StoredRecord(
                record_type=expected_type,
                id=record_id,
                title=heading.group(1),
                content=content,
                revision=revision_token(data),
                reference=RecordReference(self.backend, relative, heading.group(1), relative),
                metadata={
                    "archived": False,
                    "created": modified,
                    "legacy": True,
                    "modified": modified,
                },
            )
        try:
            metadata = json.loads(match.group("json"))
            content = match.group("body").decode()
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise RecordError("malformed_record", f"record is malformed: {path}") from error
        required = {"archived", "created", "id", "modified", "record_type", "title"}
        if (
            not isinstance(metadata, dict)
            or not required.issubset(metadata)
            or set(metadata) - (required | {"migration"})
        ):
            raise RecordError("malformed_record", f"record metadata fields are invalid: {path}")
        if "migration" in metadata and not isinstance(metadata["migration"], dict):
            raise RecordError("malformed_record", f"record migration provenance is invalid: {path}")
        if (
            not isinstance(metadata["archived"], bool)
            or not isinstance(metadata["created"], str)
            or not isinstance(metadata["modified"], str)
            or not isinstance(metadata["id"], str)
            or not isinstance(metadata["record_type"], str)
            or not isinstance(metadata["title"], str)
        ):
            raise RecordError("malformed_record", f"record metadata values are invalid: {path}")
        if metadata["record_type"] not in SUPPORTED_RECORD_TYPES:
            raise RecordError("malformed_record", f"record type is invalid: {path}")
        if metadata["id"] != path.stem and not path.stem.startswith(metadata["id"] + "-"):
            raise RecordError("malformed_record", f"record identity is invalid: {path}")
        relative = path.relative_to(self.root).as_posix()
        reference = RecordReference(
            backend=self.backend,
            id=relative,
            title=metadata["title"],
            href=relative,
        )
        return StoredRecord(
            record_type=metadata["record_type"],
            id=metadata["id"],
            title=metadata["title"],
            content=content,
            revision=revision_token(data),
            reference=reference,
            metadata={
                "archived": metadata["archived"],
                "created": metadata["created"],
                "modified": metadata["modified"],
                **({"migration": metadata["migration"]} if "migration" in metadata else {}),
            },
        )

    def _create(
        self,
        request: RecordRequest,
        destination: Path,
        prefix: str | None,
    ) -> StoredRecord:
        with self._lock(destination):
            return self._create_locked(request, destination, prefix)

    def _create_locked(
        self,
        request: RecordRequest,
        destination: Path,
        prefix: str | None,
    ) -> StoredRecord:
        destination.mkdir(parents=True, exist_ok=True)
        requested = request.semantic_id
        if requested:
            base = self._validate_id(requested)
            try:
                self._read_id(base, destination, request.record_type)
            except RecordError as error:
                if error.code != "not_found":
                    if error.code in {"duplicate_id", "malformed_record"}:
                        raise RecordError("duplicate_id", f"record id already exists: {base}") from error
                    raise
            else:
                raise RecordError("duplicate_id", f"record id already exists: {base}")
            attempt = 1
        elif prefix:
            numbers = []
            pattern = re.compile(rf"{re.escape(prefix)}-([0-9]+)(?:-.*)?\.md")
            for existing in destination.glob(f"{prefix}-*.md"):
                match = pattern.fullmatch(existing.name)
                if match:
                    numbers.append(int(match.group(1)))
            base = prefix
            attempt = max(numbers, default=0) + 1
        else:
            base = self._slug(request.title or "")
            attempt = 1
        while True:
            if prefix and not requested:
                record_id = f"{base}-{attempt:04d}"
            else:
                record_id = base if attempt == 1 else f"{base}-{attempt}"
            path = self._path(destination, record_id)
            timestamp = self.clock()
            metadata = {
                "archived": False,
                "created": timestamp,
                "id": record_id,
                "modified": timestamp,
                "record_type": request.record_type,
                "title": request.title,
            }
            data = self._serialize(metadata, request.content or "")
            try:
                with path.open("xb") as output:
                    output.write(data)
                    output.flush()
                    os.fsync(output.fileno())
                return self._deserialize(path, data, request.record_type)
            except FileExistsError as error:
                if requested:
                    raise RecordError(
                        "duplicate_id", f"record id already exists: {record_id}"
                    ) from error
                attempt += 1

    def _read_id(
        self,
        record_id: str,
        destination: Path,
        record_type: str | None = None,
    ) -> StoredRecord:
        path = self._path(destination, record_id)
        if not path.is_file():
            matches = sorted(destination.glob(f"{record_id}-*.md")) if destination.exists() else []
            if len(matches) > 1:
                raise RecordError("duplicate_id", f"record id has several owners: {record_id}")
            if matches:
                path = matches[0]
        try:
            data = path.read_bytes()
        except FileNotFoundError as error:
            raise RecordError("not_found", f"record does not exist: {record_id}") from error
        return self._deserialize(path, data, record_type)

    def _list(self, request: RecordRequest, destination: Path) -> list[StoredRecord]:
        if not destination.exists():
            return []
        query = (request.query or "").casefold()
        records = []
        for path in sorted(destination.glob("*.md")):
            record = self._deserialize(path, path.read_bytes(), request.record_type)
            if record.record_type != request.record_type or record.metadata["archived"]:
                continue
            haystack = f"{record.id}\n{record.title}\n{record.content}".casefold()
            if query and query not in haystack:
                continue
            records.append(record)
        return records

    def _update(
        self,
        request: RecordRequest,
        destination: Path,
        *,
        archived: bool,
    ) -> StoredRecord:
        with self._lock(destination):
            return self._update_locked(request, destination, archived=archived)

    def _update_locked(
        self,
        request: RecordRequest,
        destination: Path,
        *,
        archived: bool,
    ) -> StoredRecord:
        current = self._read_id(request.id or "", destination, request.record_type)
        path = self.root / current.reference.id
        before = path.read_bytes()
        if current.revision != request.expected_revision:
            raise RecordError("stale_revision", f"record changed since read: {current.id}")
        if current.metadata["archived"]:
            raise RecordError("archived_record", f"record is archived: {current.id}")
        metadata = {
            "archived": archived,
            "created": current.metadata["created"],
            "id": current.id,
            "modified": self.clock(),
            "record_type": current.record_type,
            "title": request.title if request.title is not None else current.title,
            **({"migration": current.metadata["migration"]} if "migration" in current.metadata else {}),
        }
        content = request.content if request.content is not None else current.content
        data = self._serialize(metadata, content)
        if revision_token(before) != request.expected_revision:
            raise RecordError("stale_revision", f"record changed since read: {current.id}")
        with tempfile.NamedTemporaryFile(dir=destination, delete=False) as output:
            temporary = Path(output.name)
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        try:
            if revision_token(path.read_bytes()) != request.expected_revision:
                raise RecordError("stale_revision", f"record changed since read: {current.id}")
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
        return self._deserialize(path, data, request.record_type)


def _content(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text()


def _json_file(path: str, description: str) -> Any:
    try:
        return json.loads(sys.stdin.read() if path == "-" else Path(path).read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise RecordError("invalid_request", f"cannot read {description}: {error}") from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--prefix")
    commands = parser.add_subparsers(dest="operation", required=True)

    create = commands.add_parser("create")
    create.add_argument("--record-type", default="research")
    create.add_argument("--title", required=True)
    create.add_argument("--content-file", required=True)
    create.add_argument("--semantic-id")

    read = commands.add_parser("read")
    read.add_argument("id")
    read.add_argument("--record-type", default="research")

    listing = commands.add_parser("list")
    listing.add_argument("--record-type", default="research")
    listing.add_argument("--query")

    update = commands.add_parser("update")
    update.add_argument("id")
    update.add_argument("--record-type", default="research")
    update.add_argument("--expected-revision", required=True)
    update.add_argument("--title")
    update.add_argument("--content-file")

    archive = commands.add_parser("archive")
    archive.add_argument("id")
    archive.add_argument("--record-type", default="research")
    archive.add_argument("--expected-revision", required=True)

    render = commands.add_parser("render-reference")
    render.add_argument("--reference-file", required=True)

    for name in ("migration-export", "migration-import", "migration-verify", "migration-retire"):
        command = commands.add_parser(name)
        command.add_argument("--record-type", required=True)
        if name != "migration-export":
            command.add_argument("--snapshot-file", required=True)
        if name in {"migration-verify", "migration-retire"}:
            command.add_argument("--destination-reference-file", required=True)
        if name in {"migration-import", "migration-verify"}:
            command.add_argument("--reference-map-file")

    issue_create = commands.add_parser("issue-create")
    issue_create.add_argument("--title", required=True)
    issue_create.add_argument("--body-file", required=True)
    issue_create.add_argument("--kind", required=True)
    issue_create.add_argument("--label", action="append")

    issue_read = commands.add_parser("issue-read")
    issue_read.add_argument("id")

    issue_list = commands.add_parser("issue-list")
    issue_list.add_argument("--state", choices=(*sorted(ISSUE_STATUSES), "all"))
    issue_list.add_argument("--kind")
    issue_list.add_argument("--label", action="append")
    issue_list.add_argument("--assignee")
    issue_list.add_argument("--parent-id")
    issue_list.add_argument("--query")

    issue_update = commands.add_parser("issue-update")
    issue_update.add_argument("id")
    issue_update.add_argument("--expected-revision", required=True)
    issue_update.add_argument("--title")
    issue_update.add_argument("--body-file")
    issue_update.add_argument("--kind")
    issue_update.add_argument("--label", action="append")

    for name in ("issue-comment", "issue-resolve", "issue-cancel"):
        command = commands.add_parser(name)
        command.add_argument("id")
        command.add_argument("--expected-revision", required=True)
        command.add_argument("--body-file", required=True)
        if name == "issue-comment":
            command.add_argument("--author")

    issue_claim = commands.add_parser("issue-claim")
    issue_claim.add_argument("id")
    issue_claim.add_argument("--expected-revision", required=True)
    issue_claim.add_argument("--assignee", required=True)

    issue_parent = commands.add_parser("issue-parent")
    issue_parent.add_argument("id")
    issue_parent.add_argument("--expected-revision", required=True)
    issue_parent.add_argument("--parent-id")
    issue_parent.add_argument("--remove", action="store_true")

    issue_block = commands.add_parser("issue-block")
    issue_block.add_argument("id")
    issue_block.add_argument("--expected-revision", required=True)
    issue_block.add_argument("--blocker-id", required=True)
    issue_block.add_argument("--remove", action="store_true")

    issue_frontier = commands.add_parser("issue-frontier")
    issue_frontier.add_argument("id")
    return parser


def main(arguments: list[str] | None = None) -> int:
    args = build_parser().parse_args(arguments)
    adapter = LocalMarkdownAdapter(args.root, args.backend)
    try:
        if args.operation == "render-reference":
            try:
                value = json.loads(Path(args.reference_file).read_text())
            except (OSError, json.JSONDecodeError) as error:
                raise RecordError("malformed_reference", f"cannot read reference: {error}") from error
            reference = RecordReference.from_dict(value)
            print(json.dumps({"rendered": adapter.render_reference(reference)}, indent=2, sort_keys=True))
            return 0
        if args.operation.startswith("migration-"):
            operation = args.operation.removeprefix("migration-")
            if operation == "export":
                operation = "export-history"
            snapshot = (
                _json_file(args.snapshot_file, "migration snapshot")
                if getattr(args, "snapshot_file", None)
                else None
            )
            reference = (
                RecordReference.from_dict(
                    _json_file(args.destination_reference_file, "destination reference")
                )
                if getattr(args, "destination_reference_file", None)
                else None
            )
            raw_map = (
                _json_file(args.reference_map_file, "migration reference map")
                if getattr(args, "reference_map_file", None)
                else {}
            )
            if not isinstance(raw_map, dict):
                raise RecordError("invalid_request", "migration reference map must be an object")
            reference_map = {
                key: RecordReference.from_dict(value) for key, value in raw_map.items()
            }
            result = adapter.execute_migration(
                MigrationRequest(
                    operation=operation,
                    backend=args.backend,
                    backend_type="local-markdown",
                    record_type=args.record_type,
                    destination=(
                        {"root": args.destination}
                        if args.record_type == "issues"
                        else {
                            "path": args.destination,
                            **({"prefix": args.prefix} if args.prefix is not None else {}),
                        }
                    ),
                    snapshot=snapshot,
                    destination_reference=reference,
                    reference_map=reference_map,
                )
            )
        elif args.operation.startswith("issue-"):
            operation = args.operation.removeprefix("issue-")
            labels = getattr(args, "label", None)
            request = IssueRequest(
                operation=operation,
                backend=args.backend,
                destination={"root": args.destination},
                id=getattr(args, "id", None),
                title=getattr(args, "title", None),
                body=(
                    _content(args.body_file)
                    if getattr(args, "body_file", None) is not None
                    else None
                ),
                kind=getattr(args, "kind", None),
                labels=tuple(labels) if labels is not None else None,
                expected_revision=getattr(args, "expected_revision", None),
                assignee=getattr(args, "assignee", None) or getattr(args, "author", None),
                parent_id=getattr(args, "parent_id", None),
                blocker_id=getattr(args, "blocker_id", None),
                remove=getattr(args, "remove", False),
                state=getattr(args, "state", None),
                query=getattr(args, "query", None),
            )
            result = adapter.execute_issue(request)
        else:
            request = RecordRequest(
                operation=args.operation,
                backend=args.backend,
                record_type=args.record_type,
                destination={
                    "path": args.destination,
                    **(
                        {"prefix": args.prefix}
                        if getattr(args, "prefix", None) is not None
                        else {}
                    ),
                },
                id=getattr(args, "id", None),
                title=getattr(args, "title", None),
                content=(
                    _content(args.content_file)
                    if getattr(args, "content_file", None) is not None
                    else None
                ),
                expected_revision=getattr(args, "expected_revision", None),
                semantic_id=getattr(args, "semantic_id", None),
                query=getattr(args, "query", None),
            )
            result = adapter.execute(request)
        print(json.dumps(result.as_dict(), indent=2, sort_keys=True))
        return 0
    except (OSError, RecordError) as error:
        failure = error if isinstance(error, RecordError) else RecordError("io_error", str(error))
        print(json.dumps({"error": failure.as_dict(), "ok": False}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
