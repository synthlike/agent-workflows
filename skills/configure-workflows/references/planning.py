"""Read-only deterministic consumer configuration planning."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any

from consumer import dependency_closure, inspect_skills, validate_backend_routes
import templates


ANSWER_VERSION = 1
PLAN_VERSION = 1
DIGEST = re.compile(r"sha256:[0-9a-f]{64}")
LOCAL_DESTINATIONS = {
    "issues": {"root": ".project"},
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
DEFAULT_DISABLED = {"meetings", "prototypes", "handoffs"}


class PlanError(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _strict_object(value: Any, keys: set[str], context: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise PlanError(f"{context} must contain exactly {sorted(keys)}")
    return value


def _text(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise PlanError(f"{context} must be a non-empty string")
    return value


def _relative_path(value: Any, context: str) -> str:
    text = _text(value, context)
    path = PurePosixPath(text)
    if path.is_absolute() or text != path.as_posix() or not path.parts or any(
        part in {"", ".", ".."} for part in path.parts
    ):
        raise PlanError(f"{context} must be a normalized relative path")
    return text


def _selection(value: Any, manifest: dict[str, Any]) -> list[str]:
    if not isinstance(value, dict) or "mode" not in value:
        raise PlanError("selection must be an object with a mode")
    mode = value["mode"]
    selectable = set(manifest["skills"]) - {"configure-workflows"}
    if mode == "all":
        _strict_object(value, {"mode"}, "selection")
        return sorted(selectable)
    if mode != "explicit":
        raise PlanError("selection.mode must be all or explicit")
    _strict_object(value, {"mode", "skills"}, "selection")
    skills = value["skills"]
    if (
        not isinstance(skills, list)
        or not skills
        or any(not isinstance(name, str) for name in skills)
        or len(skills) != len(set(skills))
    ):
        raise PlanError("selection.skills must be a non-empty unique string list")
    unknown = sorted(set(skills) - selectable)
    if unknown:
        raise PlanError(f"selection contains unsupported skills: {', '.join(unknown)}")
    return sorted(skills)


def _routes(answer: dict[str, Any], backends: dict[str, Any]) -> dict[str, dict[str, Any]]:
    profile = _strict_object(answer["profile"], {"name", "local_backend"}, "profile")
    if profile["name"] != "local-default":
        raise PlanError("profile.name must be local-default")
    local_backend = _text(profile["local_backend"], "profile.local_backend")
    settings = backends.get(local_backend)
    if not isinstance(settings, dict) or settings.get("type") != "local-markdown":
        raise PlanError("profile.local_backend must name a local-markdown backend")
    routes = {
        name: {
            "enabled": name not in DEFAULT_DISABLED,
            "backend": local_backend,
            "destination": dict(LOCAL_DESTINATIONS[name]),
        }
        for name in templates.RECORD_ORDER
    }
    overrides = answer["route_overrides"]
    if not isinstance(overrides, dict):
        raise PlanError("route_overrides must be an object")
    unknown = sorted(set(overrides) - set(templates.RECORD_ORDER))
    if unknown:
        raise PlanError(f"unknown route overrides: {', '.join(unknown)}")
    for name, override in overrides.items():
        if not isinstance(override, dict) or not override or not set(override) <= {
            "enabled", "backend", "destination"
        }:
            raise PlanError(
                f"route_overrides.{name} must contain enabled, backend, and/or destination"
            )
        route = routes[name]
        if "enabled" in override:
            if type(override["enabled"]) is not bool:
                raise PlanError(f"route_overrides.{name}.enabled must be boolean")
            route["enabled"] = override["enabled"]
        if "backend" in override:
            route["backend"] = _text(override["backend"], f"route_overrides.{name}.backend")
        if "destination" in override:
            if not isinstance(override["destination"], dict):
                raise PlanError(f"route_overrides.{name}.destination must be an object")
            route["destination"] = dict(override["destination"])
        elif "backend" in override and route["backend"] != local_backend:
            raise PlanError(f"route_overrides.{name} must specify destination when changing backend")
    return routes


def _prior(path: Path) -> dict[str, str]:
    if path.is_symlink():
        raise PlanError(f"managed target must not be a symlink: {path}")
    if not path.exists():
        return {"state": "absent"}
    if not path.is_file():
        raise PlanError(f"managed target collides with a non-file: {path}")
    return {"state": "file", "sha256": _digest(path.read_bytes())}


def _expected_value(prior: dict[str, str]) -> str | None:
    return prior.get("sha256") if prior["state"] == "file" else None


def directory_intent(
    root: Path,
    target_paths: list[str],
    records: dict[str, dict[str, Any]],
    backends: dict[str, dict[str, Any]],
) -> tuple[list[str], list[str]]:
    create: set[str] = set()
    for relative in target_paths:
        parent = (root / relative).parent
        while parent != root:
            if parent.is_symlink():
                raise PlanError(f"managed target parent must not be a symlink: {parent}")
            if parent.exists() and not parent.is_dir():
                raise PlanError(f"managed target parent collides with a file: {parent}")
            if not parent.exists():
                create.add(parent.relative_to(root).as_posix())
            parent = parent.parent

    absent: set[str] = set()
    for name, route in records.items():
        settings = backends[route["backend"]]
        if settings["type"] != "local-markdown":
            continue
        destination = route["destination"]
        key = "root" if name == "issues" else "path"
        relative = _relative_path(destination[key], f"records.{name}.destination.{key}")
        destination_path = root / relative
        for target in target_paths:
            target_parts = PurePosixPath(target)
            destination_parts = PurePosixPath(relative)
            if target_parts == destination_parts or destination_parts in target_parts.parents:
                raise PlanError(f"record destination collides with managed output: {relative}")
        if destination_path.is_symlink():
            raise PlanError(f"record destination must not be a symlink: {relative}")
        if destination_path.exists() and not destination_path.is_dir():
            raise PlanError(f"record destination collides with a file: {relative}")
        if not destination_path.exists():
            absent.add(relative)
    return sorted(create), sorted(absent)


def build_consumer_plan(
    consumer_root: Path,
    skill_dirs: list[Path],
    manifest: dict[str, Any],
    answer: dict[str, Any],
) -> dict[str, Any]:
    root = consumer_root.resolve()
    if not root.is_dir():
        raise PlanError(f"consumer root is not a directory: {consumer_root}")
    _strict_object(
        answer,
        {
            "answer_version", "selection", "project", "profile", "backends",
            "route_overrides", "consumer_state",
        },
        "answers",
    )
    if answer["answer_version"] != ANSWER_VERSION:
        raise PlanError(f"answer_version must be {ANSWER_VERSION}")
    project = _strict_object(
        answer["project"], {"summary", "documentation_style"}, "project"
    )
    summary = _text(project["summary"], "project.summary")
    style = _text(project["documentation_style"], "project.documentation_style")
    state = _strict_object(
        answer["consumer_state"], {"root_guidance_path", "expected_prior"},
        "consumer_state",
    )
    guidance_path = _relative_path(
        state["root_guidance_path"], "consumer_state.root_guidance_path"
    )
    if len(PurePosixPath(guidance_path).parts) != 1:
        raise PlanError("consumer_state.root_guidance_path must name one root file")
    expected_prior = state["expected_prior"]
    if not isinstance(expected_prior, dict) or any(
        not isinstance(path, str)
        or (value is not None and (not isinstance(value, str) or not DIGEST.fullmatch(value)))
        for path, value in expected_prior.items()
    ):
        raise PlanError("consumer_state.expected_prior must map paths to null or sha256 digests")

    inspection = inspect_skills(root, skill_dirs, manifest)
    if inspection.errors:
        raise PlanError("installation inspection failed: " + "; ".join(sorted(inspection.errors)))
    selected = _selection(answer["selection"], manifest)
    try:
        closure = sorted(dependency_closure(set(selected), manifest))
    except ValueError as error:
        raise PlanError(str(error)) from error
    backends = answer["backends"]
    if not isinstance(backends, dict):
        raise PlanError("backends must be an object")
    records = _routes(answer, backends)
    route_errors = validate_backend_routes(root, backends, records)
    if route_errors:
        raise PlanError("invalid backend or route intent: " + "; ".join(sorted(route_errors)))

    guidance_target = root / guidance_path
    guidance_prior = _prior(guidance_target)
    existing_guidance = guidance_target.read_bytes() if guidance_prior["state"] == "file" else b""
    inventory = {
        name: path.relative_to(root).as_posix()
        for name, path in sorted(inspection.installed.items())
    }
    try:
        rendered = templates.render_consumer_files(
            distribution=manifest["distribution"],
            selected=selected,
            skills=inventory,
            backends=backends,
            records=records,
            project_summary=summary,
            existing_root_guidance=existing_guidance,
            root_guidance_path=guidance_path,
            documentation_policy=style,
        )
    except templates.TemplateError as error:
        raise PlanError(str(error)) from error

    if set(expected_prior) != set(rendered):
        missing = sorted(set(rendered) - set(expected_prior))
        extra = sorted(set(expected_prior) - set(rendered))
        raise PlanError(f"consumer_state.expected_prior target mismatch; missing={missing}, extra={extra}")

    configure_dir = inspection.installed["configure-workflows"]
    asset_prefix = "docs/agents/backends/"
    targets: list[dict[str, Any]] = []
    for relative, content in sorted(rendered.items()):
        target = root / relative
        prior = guidance_prior if relative == guidance_path else _prior(target)
        expected = expected_prior[relative]
        if expected != _expected_value(prior):
            raise PlanError(
                f"stale consumer state for {relative}: expected {expected}, "
                f"found {_expected_value(prior)}"
            )
        destination_hash = _digest(content)
        target_entry: dict[str, Any] = {
            "destination_sha256": destination_hash,
            "path": relative,
            "prior": prior,
        }
        if relative.startswith(asset_prefix):
            name = PurePosixPath(relative).name
            source = configure_dir / "references/backends/record-store" / name
            if not source.is_file() or source.is_symlink():
                raise PlanError(f"missing immutable backend source asset: {name}")
            source_content = source.read_bytes()
            if source_content != content:
                raise PlanError(f"renderer asset differs from immutable source: {name}")
            target_entry.update({
                "kind": "copy",
                "source": {
                    "path": source.relative_to(root).as_posix(),
                    "sha256": _digest(source_content),
                },
            })
        else:
            try:
                exact_text = content.decode("utf-8")
            except UnicodeDecodeError as error:
                raise PlanError(f"generated text is not UTF-8: {relative}") from error
            target_entry.update({"kind": "text", "content": exact_text})
        targets.append(target_entry)

    target_paths = [target["path"] for target in targets]
    directories_to_create, directories_left_absent = directory_intent(
        root, target_paths, records, backends
    )
    manifest_hash = _digest(canonical_json(manifest))
    plan: dict[str, Any] = {
        "plan_version": PLAN_VERSION,
        "consumer_root": str(root),
        "distribution": {
            "source": manifest["distribution"]["source"],
            "version": manifest["distribution"]["version"],
            "manifest_sha256": manifest_hash,
        },
        "installation": {
            "closure": closure,
            "selected": selected,
            "skills": {
                name: {
                    "model_invocation": manifest["skills"][name]["model_invocation"],
                    "path": inventory[name],
                }
                for name in sorted(inventory)
            },
        },
        "intent": {
            "answer_version": ANSWER_VERSION,
            "backends": backends,
            "profile": answer["profile"],
            "project": project,
            "records": records,
            "root_guidance_path": guidance_path,
        },
        "directories_to_create": directories_to_create,
        "directories_left_absent": directories_left_absent,
        "targets": targets,
    }
    plan["digest"] = _digest(canonical_json(plan))
    return plan
