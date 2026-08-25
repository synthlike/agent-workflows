"""Transactional application of approved deterministic consumer plans."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile
from typing import Any, Callable

from consumer import dependency_closure, inspect_skills, validate_backend_routes, verify_consumer
from planning import (
    DIGEST,
    PLAN_VERSION,
    canonical_json,
    directory_intent,
)
import templates


class ApplyError(ValueError):
    pass


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ApplyError(f"duplicate plan key: {key}")
        result[key] = value
    return result


def parse_canonical_plan(data: bytes, expected_digest: str) -> dict[str, Any]:
    if not DIGEST.fullmatch(expected_digest):
        raise ApplyError("expected digest must use sha256:<lowercase-hex>")
    try:
        plan = json.loads(data, object_pairs_hook=_unique_object)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ApplyError(f"invalid plan JSON: {error}") from error
    if not isinstance(plan, dict):
        raise ApplyError("plan must be a JSON object")
    if canonical_json(plan) != data:
        raise ApplyError("plan file must contain exact canonical JSON bytes")
    if plan.get("digest") != expected_digest:
        raise ApplyError("plan digest does not match the exact expected digest")
    body = dict(plan)
    body.pop("digest", None)
    if _digest(canonical_json(body)) != expected_digest:
        raise ApplyError("plan digest is invalid")
    return plan


def _strict(value: Any, fields: set[str], context: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ApplyError(f"{context} must contain exactly {sorted(fields)}")
    return value


def _relative(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise ApplyError(f"{context} must be a non-empty relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or value != path.as_posix() or any(
        part in {"", ".", ".."} for part in path.parts
    ):
        raise ApplyError(f"{context} must be a normalized relative path")
    return value


def _current_prior(path: Path) -> dict[str, str]:
    if path.is_symlink():
        raise ApplyError(f"managed target must not be a symlink: {path}")
    if not path.exists():
        return {"state": "absent"}
    if not path.is_file():
        raise ApplyError(f"managed target collides with a non-file: {path}")
    return {"state": "file", "sha256": _digest(path.read_bytes())}


def _validate_prior(value: Any, context: str) -> dict[str, str]:
    if value == {"state": "absent"}:
        return value
    if (
        isinstance(value, dict)
        and set(value) == {"state", "sha256"}
        and value.get("state") == "file"
        and isinstance(value.get("sha256"), str)
        and DIGEST.fullmatch(value["sha256"])
    ):
        return value
    raise ApplyError(f"{context} must describe absent or sha256-bound file state")


def _validate_string_list(value: Any, context: str) -> list[str]:
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) for item in value)
        or value != sorted(set(value))
    ):
        raise ApplyError(f"{context} must be a sorted unique string list")
    return value


def _validate_plan_schema(plan: dict[str, Any]) -> None:
    _strict(
        plan,
        {
            "plan_version", "digest", "consumer_root", "distribution", "installation",
            "intent", "directories_to_create", "directories_left_absent", "targets",
        },
        "plan",
    )
    if plan["plan_version"] != PLAN_VERSION:
        raise ApplyError(f"plan_version must be {PLAN_VERSION}")
    if not isinstance(plan["consumer_root"], str) or not plan["consumer_root"]:
        raise ApplyError("consumer_root must be a non-empty string")
    distribution = _strict(
        plan["distribution"], {"source", "version", "manifest_sha256"}, "distribution"
    )
    if any(not isinstance(distribution[key], str) or not distribution[key] for key in distribution):
        raise ApplyError("distribution values must be non-empty strings")
    if not DIGEST.fullmatch(distribution["manifest_sha256"]):
        raise ApplyError("distribution.manifest_sha256 must be a sha256 digest")
    installation = _strict(
        plan["installation"], {"closure", "selected", "skills"}, "installation"
    )
    _validate_string_list(installation["closure"], "installation.closure")
    _validate_string_list(installation["selected"], "installation.selected")
    if not isinstance(installation["skills"], dict) or not installation["skills"]:
        raise ApplyError("installation.skills must be a non-empty object")
    for name, entry in installation["skills"].items():
        if not isinstance(name, str) or not name:
            raise ApplyError("installation skill names must be non-empty strings")
        _strict(entry, {"model_invocation", "path"}, f"installation.skills.{name}")
        if entry["model_invocation"] not in {"enabled", "manual"}:
            raise ApplyError(f"installation.skills.{name}.model_invocation is invalid")
        _relative(entry["path"], f"installation.skills.{name}.path")
    intent = _strict(
        plan["intent"],
        {"answer_version", "backends", "profile", "project", "records", "root_guidance_path"},
        "intent",
    )
    if intent["answer_version"] != 1:
        raise ApplyError("intent.answer_version must be 1")
    _strict(intent["project"], {"summary", "documentation_style"}, "intent.project")
    profile = _strict(intent["profile"], {"name", "local_backend"}, "intent.profile")
    if not isinstance(intent["backends"], dict) or not isinstance(intent["records"], dict):
        raise ApplyError("intent backends and records must be objects")
    if profile["name"] != "local-default":
        raise ApplyError("intent.profile.name must be local-default")
    local_backend = profile["local_backend"]
    local_settings = (
        intent["backends"].get(local_backend) if isinstance(local_backend, str) else None
    )
    if not isinstance(local_settings, dict) or local_settings.get("type") != "local-markdown":
        raise ApplyError("intent.profile.local_backend must name a local-markdown backend")
    guidance = _relative(intent["root_guidance_path"], "intent.root_guidance_path")
    if len(PurePosixPath(guidance).parts) != 1:
        raise ApplyError("intent.root_guidance_path must name one root file")
    for key in ("summary", "documentation_style"):
        if not isinstance(intent["project"][key], str) or not intent["project"][key]:
            raise ApplyError(f"intent.project.{key} must be a non-empty string")
    _validate_string_list(plan["directories_to_create"], "directories_to_create")
    _validate_string_list(plan["directories_left_absent"], "directories_left_absent")
    targets = plan["targets"]
    if not isinstance(targets, list) or not targets:
        raise ApplyError("targets must be a non-empty list")
    paths = []
    for index, target in enumerate(targets):
        context = f"targets[{index}]"
        if not isinstance(target, dict):
            raise ApplyError(f"{context} must be an object")
        kind = target.get("kind")
        fields = {"kind", "path", "destination_sha256", "prior"}
        fields |= {"content"} if kind == "text" else {"source"} if kind == "copy" else set()
        if kind not in {"text", "copy"}:
            raise ApplyError(f"{context}.kind must be text or copy")
        _strict(target, fields, context)
        path = _relative(target["path"], f"{context}.path")
        paths.append(path)
        if not isinstance(target["destination_sha256"], str) or not DIGEST.fullmatch(
            target["destination_sha256"]
        ):
            raise ApplyError(f"{context}.destination_sha256 must be a sha256 digest")
        _validate_prior(target["prior"], f"{context}.prior")
        if kind == "text" and not isinstance(target["content"], str):
            raise ApplyError(f"{context}.content must be a string")
        if kind == "copy":
            source = _strict(target["source"], {"path", "sha256"}, f"{context}.source")
            _relative(source["path"], f"{context}.source.path")
            if not isinstance(source["sha256"], str) or not DIGEST.fullmatch(source["sha256"]):
                raise ApplyError(f"{context}.source.sha256 must be a sha256 digest")
    if paths != sorted(set(paths)):
        raise ApplyError("target paths must be sorted and unique")


def _validate_and_materialize(
    root: Path,
    plan: dict[str, Any],
    manifest: dict[str, Any],
) -> tuple[list[Path], dict[str, bytes]]:
    if Path(plan["consumer_root"]) != root:
        raise ApplyError("plan consumer_root does not match --consumer-root")
    distribution = plan["distribution"]
    if distribution["source"] != manifest["distribution"]["source"] or distribution[
        "version"
    ] != manifest["distribution"]["version"]:
        raise ApplyError("plan release identity does not match the installed manifest")
    if distribution["manifest_sha256"] != _digest(canonical_json(manifest)):
        raise ApplyError("plan manifest hash does not match the installed manifest")

    inventory = plan["installation"]["skills"]
    if set(inventory) != set(manifest["skills"]):
        raise ApplyError("plan installed inventory is incomplete or unexpected")
    skill_dirs = [root / inventory[name]["path"] for name in sorted(inventory)]
    inspection = inspect_skills(root, skill_dirs, manifest)
    if inspection.errors:
        raise ApplyError("installed inventory validation failed: " + "; ".join(sorted(inspection.errors)))
    for name, entry in inventory.items():
        if inspection.installed[name] != (root / entry["path"]).resolve():
            raise ApplyError(f"plan inventory path changed for {name}")
        if entry["model_invocation"] != manifest["skills"][name]["model_invocation"]:
            raise ApplyError(f"plan invocation policy changed for {name}")
    selected = plan["installation"]["selected"]
    try:
        closure = sorted(dependency_closure(set(selected), manifest))
    except ValueError as error:
        raise ApplyError(str(error)) from error
    if closure != plan["installation"]["closure"]:
        raise ApplyError("plan dependency closure is invalid")
    for target in plan["targets"]:
        if _current_prior(root / target["path"]) != target["prior"]:
            raise ApplyError(f"stale target state: {target['path']}")

    intent = plan["intent"]
    route_errors = validate_backend_routes(root, intent["backends"], intent["records"])
    if route_errors:
        raise ApplyError("invalid planned backends or routes: " + "; ".join(sorted(route_errors)))
    guidance_path = intent["root_guidance_path"]
    guidance_target = root / guidance_path
    guidance_prior = _current_prior(guidance_target)
    existing_guidance = guidance_target.read_bytes() if guidance_prior["state"] == "file" else b""
    skill_paths = {name: inventory[name]["path"] for name in sorted(inventory)}
    try:
        rendered = templates.render_consumer_files(
            distribution=manifest["distribution"],
            selected=selected,
            skills=skill_paths,
            backends=intent["backends"],
            records=intent["records"],
            project_summary=intent["project"]["summary"],
            existing_root_guidance=existing_guidance,
            root_guidance_path=guidance_path,
            documentation_policy=intent["project"]["documentation_style"],
        )
    except templates.TemplateError as error:
        raise ApplyError(str(error)) from error
    target_by_path = {target["path"]: target for target in plan["targets"]}
    if set(target_by_path) != set(rendered):
        raise ApplyError("planned target set differs from canonical rendered target set")

    materialized: dict[str, bytes] = {}
    configure_path = inventory["configure-workflows"]["path"]
    for relative, canonical_content in sorted(rendered.items()):
        target = target_by_path[relative]
        if target["kind"] == "text":
            content = target["content"].encode("utf-8")
            if content != canonical_content:
                raise ApplyError(f"planned text differs from canonical rendering: {relative}")
        else:
            expected_source = (
                PurePosixPath(configure_path)
                / "references/backends/record-store"
                / PurePosixPath(relative).name
            ).as_posix()
            if target["source"]["path"] != expected_source:
                raise ApplyError(f"planned source path is invalid: {relative}")
            source = root / expected_source
            if source.is_symlink() or not source.is_file():
                raise ApplyError(f"planned source asset is missing or unsafe: {expected_source}")
            content = source.read_bytes()
            if _digest(content) != target["source"]["sha256"]:
                raise ApplyError(f"planned source asset hash is stale: {expected_source}")
            if content != canonical_content:
                raise ApplyError(f"planned source differs from canonical asset: {expected_source}")
        if _digest(content) != target["destination_sha256"]:
            raise ApplyError(f"planned destination hash is invalid: {relative}")
        current = _current_prior(root / relative)
        if current != target["prior"]:
            raise ApplyError(f"stale target state: {relative}")
        materialized[relative] = content

    target_paths = sorted(materialized)
    create, absent = directory_intent(root, target_paths, intent["records"], intent["backends"])
    if create != plan["directories_to_create"]:
        raise ApplyError("planned directory creation state is stale or invalid")
    if absent != plan["directories_left_absent"]:
        raise ApplyError("planned lazy record-directory state is stale or invalid")
    for relative in create + absent:
        _relative(relative, "planned directory")
    return skill_dirs, materialized


def _rollback(
    root: Path,
    targets: list[dict[str, Any]],
    written: list[str],
    backups: dict[str, Path],
    created_directories: list[Path],
) -> list[str]:
    errors: list[str] = []
    target_by_path = {target["path"]: target for target in targets}
    for relative in reversed(written):
        target_path = root / relative
        prior = target_by_path[relative]["prior"]
        try:
            if prior["state"] == "absent":
                if target_path.is_file() or target_path.is_symlink():
                    target_path.unlink()
            else:
                backup = backups[relative]
                os.replace(backup, target_path)
        except OSError as error:
            errors.append(f"could not restore {relative}: {error}")
    for directory in reversed(created_directories):
        try:
            directory.rmdir()
        except OSError as error:
            if directory.exists():
                errors.append(
                    f"could not remove created directory {directory.relative_to(root)}: {error}"
                )
    for target in targets:
        try:
            if _current_prior(root / target["path"]) != target["prior"]:
                errors.append(f"restored state differs for {target['path']}")
        except ApplyError as error:
            errors.append(str(error))
    return errors


def apply_consumer_plan(
    consumer_root: Path,
    plan: dict[str, Any],
    manifest: dict[str, Any],
    *,
    verifier: Callable[[Path, list[Path], dict[str, Any]], Any] = verify_consumer,
    after_write: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    root = consumer_root.resolve()
    if not root.is_dir():
        raise ApplyError(f"consumer root is not a directory: {consumer_root}")
    _validate_plan_schema(plan)
    skill_dirs, materialized = _validate_and_materialize(root, plan, manifest)
    target_by_path = {target["path"]: target for target in plan["targets"]}
    changed = [
        path for path in sorted(materialized)
        if target_by_path[path]["prior"].get("sha256") != target_by_path[path]["destination_sha256"]
    ]
    unchanged = sorted(set(materialized) - set(changed))

    stage_root = Path(tempfile.mkdtemp(prefix=".agent-workflows-stage-", dir=root.parent))
    if stage_root.stat().st_dev != root.stat().st_dev:
        shutil.rmtree(stage_root, ignore_errors=True)
        raise ApplyError("staging directory is not on the destination filesystem")
    staged: dict[str, Path] = {}
    backups: dict[str, Path] = {}
    try:
        outputs = stage_root / "outputs"
        backups_root = stage_root / "backups"
        outputs.mkdir()
        backups_root.mkdir()
        for index, relative in enumerate(sorted(materialized)):
            staged_path = outputs / str(index)
            staged_path.write_bytes(materialized[relative])
            if _digest(staged_path.read_bytes()) != target_by_path[relative]["destination_sha256"]:
                raise ApplyError(f"staged output hash differs: {relative}")
            staged[relative] = staged_path
        for index, relative in enumerate(changed):
            if target_by_path[relative]["prior"]["state"] == "file":
                backup = backups_root / str(index)
                shutil.copy2(root / relative, backup)
                backups[relative] = backup
        # Close the validation-to-write window as far as a local process can.
        _validate_and_materialize(root, plan, manifest)

        created_directories: list[Path] = []
        written: list[str] = []
        try:
            for relative in sorted(
                plan["directories_to_create"], key=lambda value: (len(PurePosixPath(value).parts), value)
            ):
                directory = root / relative
                directory.mkdir()
                created_directories.append(directory)
            for relative in changed:
                os.replace(staged[relative], root / relative)
                written.append(relative)
                if after_write is not None:
                    after_write(relative)
            verification = verifier(root, skill_dirs, manifest)
            if verification.errors:
                raise ApplyError(
                    "post-apply verification failed: " + "; ".join(sorted(verification.errors))
                )
            unexpectedly_created = [
                relative for relative in plan["directories_left_absent"]
                if (root / relative).exists() or (root / relative).is_symlink()
            ]
            if unexpectedly_created:
                raise ApplyError(
                    "lazy record directories were created unexpectedly: "
                    + ", ".join(unexpectedly_created)
                )
        except Exception as error:
            recovery_errors = _rollback(
                root, plan["targets"], written, backups, created_directories
            )
            if recovery_errors:
                raise ApplyError(
                    f"apply failed: {error}; rollback incomplete: {'; '.join(recovery_errors)}"
                ) from error
            raise ApplyError(f"apply failed: {error}; rollback succeeded") from error

        return {
            "ok": True,
            "digest": plan["digest"],
            "files": sorted(materialized),
            "changed": changed,
            "unchanged": unchanged,
            "directories_created": [
                path.relative_to(root).as_posix() for path in created_directories
            ],
            "directories_left_absent": plan["directories_left_absent"],
            "verification": verification.as_dict(),
        }
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)
