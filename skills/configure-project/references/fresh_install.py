"""Non-destructive fresh-install planning and apply operations."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
from typing import Any, Callable

from consumer import dependency_closure, inspect_skills


PLAN_VERSION = 1


class FreshInstallError(ValueError):
    """A fresh-install plan cannot be generated or applied safely."""


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _relative_destination(root: Path, value: Path, name: str) -> tuple[Path | None, str | None]:
    resolved_root = root.resolve()
    candidate = value if value.is_absolute() else resolved_root / value
    resolved = candidate.resolve()
    try:
        relative = resolved.relative_to(resolved_root)
    except ValueError:
        return None, f"destination for {name} escapes the consumer root: {value}"
    if resolved.name != name:
        return None, f"destination for {name} has wrong directory name: {value}"
    return resolved, relative.as_posix()


def _plan_id(body: dict[str, Any]) -> str:
    return _sha256(canonical_json(body))


def _bundle_skill_files(bundle: Any, name: str) -> list[dict[str, Any]]:
    prefix = PurePosixPath(bundle.root_name) / "skills" / name
    files = []
    for member in sorted(bundle.files, key=lambda path: path.as_posix()):
        try:
            relative = member.relative_to(prefix)
        except ValueError:
            continue
        files.append(
            {
                "path": relative.as_posix(),
                "sha256": _sha256(bundle.files[member]),
            }
        )
    return files


def plan_fresh_install(
    consumer_root: Path,
    discovered_skill_dirs: list[Path],
    selected: set[str],
    installed_manifest: dict[str, Any],
    bundle: Any,
    destination_overrides: dict[str, Path] | None = None,
) -> dict[str, Any]:
    root = consumer_root.resolve()
    errors: list[str] = []
    if bundle.manifest != installed_manifest:
        errors.append("release bundle manifest does not match installed configure-project")
    try:
        selected_closure = dependency_closure(selected, installed_manifest)
    except ValueError as error:
        selected_closure = set()
        errors.append(str(error))
    inspection = inspect_skills(
        root,
        discovered_skill_dirs,
        installed_manifest,
        check_dependencies=False,
    )
    errors.extend(inspection.errors)
    installed = set(inspection.installed)
    unexpected = installed - selected_closure if selected_closure else installed
    required = set(selected_closure)
    for name in sorted(unexpected & installed_manifest["skills"].keys()):
        required.update(dependency_closure({name}, installed_manifest))
    missing = required - installed
    configure_path = inspection.installed.get("configure-project")
    if configure_path is None:
        errors.append("cannot choose default destinations without discovered configure-project")
    overrides = destination_overrides or {}
    unknown_overrides = set(overrides) - missing
    if unknown_overrides:
        errors.append(
            "destination overrides name skills that are not missing: "
            + ", ".join(sorted(unknown_overrides))
        )
    destinations: dict[str, str] = {}
    destination_paths: dict[str, Path] = {}
    seen: dict[Path, str] = {}
    for name in sorted(missing):
        proposed = overrides.get(name)
        if proposed is None and configure_path is not None:
            proposed = configure_path.parent / name
        if proposed is None:
            continue
        destination, relative = _relative_destination(root, proposed, name)
        if destination is None or relative is None:
            errors.append(relative or f"invalid destination for {name}: {proposed}")
            continue
        if destination in seen:
            errors.append(f"destination collision for {seen[destination]} and {name}: {relative}")
        seen[destination] = name
        if destination.exists():
            errors.append(f"destination for missing skill {name} is occupied: {relative}")
        destinations[name] = relative
        destination_paths[name] = destination
    if set(destinations) != missing:
        unresolved = missing - set(destinations)
        if unresolved:
            errors.append(f"missing skills have no valid destination: {', '.join(sorted(unresolved))}")

    discovered = {
        name: path.relative_to(root).as_posix()
        for name, path in sorted(inspection.installed.items())
    }
    inventory = {**discovered, **destinations}
    actions = [
        {
            "destination": destinations[name],
            "files": _bundle_skill_files(bundle, name),
            "skill": name,
            "source": f"skills/{name}",
            "type": "create-skill",
        }
        for name in sorted(destinations)
    ]
    body: dict[str, Any] = {
        "actions": actions,
        "bundle_sha256": bundle.digest,
        "closure": sorted(selected_closure),
        "configuration": {
            "distribution": installed_manifest["distribution"],
            "installation": {
                "selected": sorted(selected),
                "skills": dict(sorted(inventory.items())),
            },
            "schema_version": 2,
        },
        "consumer_root": str(root),
        "destination_overrides": {
            name: path.as_posix() for name, path in sorted(overrides.items())
        },
        "discovered": discovered,
        "errors": sorted(set(errors)),
        "guidance_changes": [
            ".agents/workflows.yaml",
            "docs/agents/issue-tracker.md",
            "docs/agents/workflows.md",
            "AGENTS.md or equivalent",
        ],
        "missing": sorted(missing),
        "operation": "fresh-configuration",
        "plan_version": PLAN_VERSION,
        "release": installed_manifest["distribution"],
        "required_installed": sorted(required),
        "selected": sorted(selected),
        "unexpected": sorted(unexpected),
    }
    return {**body, "plan_id": _plan_id(body)}


def _validate_plan_shape(plan: dict[str, Any]) -> None:
    required = {
        "actions",
        "bundle_sha256",
        "closure",
        "configuration",
        "consumer_root",
        "destination_overrides",
        "discovered",
        "errors",
        "guidance_changes",
        "missing",
        "operation",
        "plan_id",
        "plan_version",
        "release",
        "required_installed",
        "selected",
        "unexpected",
    }
    if set(plan) != required:
        raise FreshInstallError("fresh-install plan has missing or unknown fields")
    if plan.get("operation") != "fresh-configuration" or plan.get("plan_version") != PLAN_VERSION:
        raise FreshInstallError("fresh-install plan version or operation is unsupported")
    list_fields = (
        "actions",
        "closure",
        "errors",
        "guidance_changes",
        "missing",
        "required_installed",
        "selected",
        "unexpected",
    )
    mapping_fields = (
        "configuration",
        "destination_overrides",
        "discovered",
        "release",
    )
    if any(not isinstance(plan[field], list) for field in list_fields) or any(
        not isinstance(plan[field], dict) for field in mapping_fields
    ):
        raise FreshInstallError("fresh-install plan has invalid field types")
    if any(
        not isinstance(item, str)
        for field in ("closure", "errors", "guidance_changes", "missing", "required_installed", "selected", "unexpected")
        for item in plan[field]
    ):
        raise FreshInstallError("fresh-install plan lists must contain strings")
    if any(
        not isinstance(key, str) or not isinstance(value, str)
        for field in ("destination_overrides", "discovered")
        for key, value in plan[field].items()
    ):
        raise FreshInstallError("fresh-install plan path mappings are invalid")
    if (
        not isinstance(plan.get("consumer_root"), str)
        or not isinstance(plan.get("bundle_sha256"), str)
        or not isinstance(plan.get("plan_id"), str)
    ):
        raise FreshInstallError("fresh-install plan identities are invalid")
    body = {key: value for key, value in plan.items() if key != "plan_id"}
    if plan.get("plan_id") != _plan_id(body):
        raise FreshInstallError("fresh-install plan identity is invalid")


def apply_fresh_install(
    plan: dict[str, Any],
    consumer_root: Path,
    bundle: Any,
    installed_manifest: dict[str, Any],
    *,
    before_publish: Callable[[str, Path], None] | None = None,
) -> list[str]:
    _validate_plan_shape(plan)
    if plan["errors"]:
        raise FreshInstallError("cannot apply a fresh-install plan that contains errors")
    root = consumer_root.resolve()
    if plan["consumer_root"] != str(root):
        raise FreshInstallError("fresh-install plan belongs to a different consumer root")
    if plan["bundle_sha256"] != bundle.digest or plan["release"] != bundle.manifest["distribution"]:
        raise FreshInstallError("release bundle changed after planning")
    discovered_dirs = [root / path for path in plan["discovered"].values()]
    overrides = {name: Path(path) for name, path in plan["destination_overrides"].items()}
    try:
        current = plan_fresh_install(
            root,
            discovered_dirs,
            set(plan["selected"]),
            installed_manifest,
            bundle,
            overrides,
        )
    except (KeyError, TypeError, ValueError) as error:
        raise FreshInstallError(f"fresh-install plan inputs are invalid: {error}") from error
    if current != plan:
        raise FreshInstallError("fresh-install inputs changed after planning")

    destinations = {
        action["skill"]: root / action["destination"] for action in plan["actions"]
    }
    for name, destination in destinations.items():
        if destination.exists():
            raise FreshInstallError(f"destination became occupied for {name}: {destination}")

    stages: dict[str, Path] = {}
    created: list[str] = []
    try:
        for name, destination in sorted(destinations.items()):
            destination.parent.mkdir(parents=True, exist_ok=True)
            stage = destination.parent / f".{name}.agent-workflows-stage-{plan['plan_id'][:12]}"
            if stage.exists():
                raise FreshInstallError(f"staging path is occupied for {name}: {stage}")
            stage.mkdir()
            stages[name] = stage
            prefix = PurePosixPath(bundle.root_name) / "skills" / name
            members = []
            for member, data in sorted(bundle.files.items(), key=lambda item: item[0].as_posix()):
                try:
                    relative = member.relative_to(prefix)
                except ValueError:
                    continue
                target = stage / Path(relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                target.chmod(bundle.modes[member])
                members.append(relative.as_posix())
            expected = {
                item["path"]
                for action in plan["actions"]
                if action["skill"] == name
                for item in action["files"]
            }
            if set(members) != expected:
                raise FreshInstallError(f"staged files changed for {name}")
            for item in next(action for action in plan["actions"] if action["skill"] == name)["files"]:
                if _sha256((stage / item["path"]).read_bytes()) != item["sha256"]:
                    raise FreshInstallError(f"staged file digest mismatch for {name}/{item['path']}")
        for name, destination in sorted(destinations.items()):
            if before_publish is not None:
                before_publish(name, destination)
            if destination.exists():
                raise FreshInstallError(f"destination became occupied for {name}: {destination}")
            stages[name].rename(destination)
            created.append(destination.relative_to(root).as_posix())
    except Exception as error:
        for stage in stages.values():
            if stage.exists():
                shutil.rmtree(stage, ignore_errors=True)
        cleanup = ", ".join(created) if created else "none"
        if isinstance(error, FreshInstallError):
            message = str(error)
        else:
            message = f"unexpected apply failure: {error}"
        raise FreshInstallError(
            f"{message}; created skill directories requiring cleanup: {cleanup}"
        ) from error
    return created
