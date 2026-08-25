#!/usr/bin/env python3
"""Pure deterministic rendering for distribution-managed consumer files."""

from __future__ import annotations

from pathlib import Path
import json
import re
from typing import Any


HERE = Path(__file__).resolve().parent
TEMPLATE_DIR = HERE / "templates"
BACKEND_DIR = HERE / "backends/record-store"
RECORD_ORDER = (
    "issues", "domain", "arps", "rfcs", "specs", "meetings", "research",
    "questionnaires", "technical_baselines", "problem_framing", "prototypes",
    "handoffs",
)
BACKEND_FIELDS = {
    "local-markdown": (),
    "github": ("repository", "login"),
    "bear": ("command", "workspace"),
}
DESTINATION_FIELDS = {
    "local-markdown": {"issues": ("root",), "default": ("path",), "arps": ("path", "prefix"), "rfcs": ("path", "prefix")},
    "github": {"default": ("label",)},
    "bear": {"default": ("tag",)},
}
BACKEND_ASSETS = {
    "local-markdown": ("local-markdown.md", "local-markdown.py"),
    "github": ("github.md", "github.py"),
    "bear": ("bear.md", "bear.py"),
}
NAME = re.compile(r"[a-z][a-z0-9_-]*")
START = b"<!-- agent-workflows:start -->"
END = b"<!-- agent-workflows:end -->"
DEFAULT_DOCUMENTATION_POLICY = (
    "Write clear, direct documentation. Prefer active voice, short sentences, explicit "
    "references, and established domain terms. Avoid idioms, unnecessary synonyms, and "
    "ambiguous pronouns. Use one action per procedural step."
)


class TemplateError(ValueError):
    pass


def _text(name: str) -> str:
    return (TEMPLATE_DIR / name).read_text()


def _fill(name: str, values: dict[str, str]) -> bytes:
    text = _text(name)
    placeholder = re.compile(r"{{([a-z_]+)}}")
    expected = set(placeholder.findall(text))
    if expected != set(values):
        missing = sorted(expected - set(values))
        extra = sorted(set(values) - expected)
        raise TemplateError(
            f"template values for {name} do not match; missing={missing}, extra={extra}"
        )
    return placeholder.sub(lambda match: values[match.group(1)], text).encode()


def _string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise TemplateError(f"{context} must be a non-empty string")
    return value


def _yaml(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _managed_guidance(existing: bytes, section: bytes) -> bytes:
    starts = existing.count(START)
    ends = existing.count(END)
    if starts != ends or starts > 1:
        raise TemplateError("root guidance has ambiguous agent-workflows managed markers")
    if starts == 1:
        start = existing.index(START)
        try:
            end = existing.index(END, start) + len(END)
        except ValueError as error:
            raise TemplateError("root guidance has ambiguous agent-workflows managed markers") from error
        if section.endswith(b"\n") and existing[end:].startswith(b"\n"):
            section = section[:-1]
        return existing[:start] + section + existing[end:]
    if not existing:
        return section
    separator = b"" if existing.endswith(b"\n\n") else b"\n" if existing.endswith(b"\n") else b"\n\n"
    return existing + separator + section


def _destination_fields(backend_type: str, record: str) -> tuple[str, ...]:
    choices = DESTINATION_FIELDS[backend_type]
    return choices.get(record, choices["default"])


def render_consumer_files(
    *,
    distribution: dict[str, Any],
    selected: list[str],
    skills: dict[str, str],
    backends: dict[str, dict[str, Any]],
    records: dict[str, dict[str, Any]],
    project_summary: str = "Project collaboration and persistence intent is recorded in the approved configuration plan.",
    existing_root_guidance: bytes = b"",
    root_guidance_path: str = "AGENTS.md",
    documentation_policy: str = DEFAULT_DOCUMENTATION_POLICY,
) -> dict[str, bytes]:
    """Return canonical target-path bytes without writing to the consumer."""
    source = _string(distribution.get("source"), "distribution.source")
    version = _string(distribution.get("version"), "distribution.version")
    guidance_path = Path(root_guidance_path)
    if (
        not root_guidance_path
        or guidance_path.is_absolute()
        or len(guidance_path.parts) != 1
        or guidance_path.name in {".", ".."}
    ):
        raise TemplateError("root_guidance_path must name one consumer-root file")
    if not selected or selected != sorted(set(selected)):
        raise TemplateError("selected skills must be a non-empty sorted unique list")
    if set(records) != set(RECORD_ORDER):
        raise TemplateError("records must contain all twelve canonical record keys")
    if not backends:
        raise TemplateError("at least one backend is required")

    selected_lines = []
    for name in selected:
        if not NAME.fullmatch(name):
            raise TemplateError(f"invalid selected skill name: {name}")
        selected_lines.append(f"    - {_yaml(name)}")
    missing_selected = sorted(set(selected) - set(skills))
    if missing_selected:
        raise TemplateError(f"selected skills missing from installation: {', '.join(missing_selected)}")
    skill_lines = []
    for name in sorted(skills):
        if not NAME.fullmatch(name):
            raise TemplateError(f"invalid installed skill name: {name}")
        skill_lines.append(f"    {name}: {_yaml(_string(skills[name], f'installation.skills.{name}'))}")

    backend_lines: list[str] = []
    backend_types: dict[str, str] = {}
    for instance in sorted(backends):
        if not NAME.fullmatch(instance):
            raise TemplateError(f"invalid backend instance name: {instance}")
        settings = backends[instance]
        backend_type = settings.get("type") if isinstance(settings, dict) else None
        if backend_type not in BACKEND_FIELDS:
            raise TemplateError(f"unsupported backend type for {instance}: {backend_type}")
        expected = {"type", *BACKEND_FIELDS[backend_type]}
        if set(settings) != expected:
            raise TemplateError(f"{instance} backend fields must be {sorted(expected)}")
        backend_types[instance] = backend_type
        backend_lines.extend((f"  {instance}:", f"    type: {_yaml(backend_type)}"))
        for field in BACKEND_FIELDS[backend_type]:
            backend_lines.append(f"    {field}: {_yaml(_string(settings[field], f'backends.{instance}.{field}'))}")

    record_lines: list[str] = []
    route_rows: list[str] = []
    used_types: set[str] = set()
    for record in RECORD_ORDER:
        route = records[record]
        if not isinstance(route, dict) or set(route) != {"enabled", "backend", "destination"}:
            raise TemplateError(f"{record} route must contain enabled, backend, and destination")
        if type(route["enabled"]) is not bool:
            raise TemplateError(f"{record}.enabled must be boolean")
        instance = route["backend"]
        if instance not in backend_types:
            raise TemplateError(f"{record} uses unknown backend instance: {instance}")
        backend_type = backend_types[instance]
        if backend_type == "bear" and record == "issues":
            raise TemplateError("bear does not support issues")
        destination = route["destination"]
        expected_fields = _destination_fields(backend_type, record)
        if not isinstance(destination, dict) or set(destination) != set(expected_fields):
            raise TemplateError(f"{record} destination fields must be {list(expected_fields)}")
        used_types.add(backend_type)
        record_lines.extend((
            f"  {record}:",
            f"    enabled: {'true' if route['enabled'] else 'false'}",
            f"    backend: {_yaml(instance)}",
            "    destination:",
        ))
        rendered_destination = []
        for field in expected_fields:
            value = _string(destination[field], f"records.{record}.destination.{field}")
            record_lines.append(f"      {field}: {_yaml(value)}")
            rendered_destination.append(f"{field} `{value}`")
        route_rows.append(
            f"| `{record}` | {'Enabled' if route['enabled'] else 'Disabled'} | "
            f"`{instance}` (`{backend_type}`) | {', '.join(rendered_destination)} |"
        )

    assets = ["contract.py"]
    for backend_type in sorted(used_types):
        assets.extend(BACKEND_ASSETS[backend_type])
    asset_lines = [f"- `docs/agents/backends/{name}`" for name in assets]
    selected_guidance = "\n".join(f"- `{name}`" for name in selected)
    files = {
        ".agents/workflows.yaml": _fill("workflows.yaml.tmpl", {
            "distribution_source": _yaml(source),
            "distribution_version": _yaml(version),
            "selected_skills": "\n".join(selected_lines),
            "installed_skills": "\n".join(skill_lines),
            "backends": "\n".join(backend_lines),
            "records": "\n".join(record_lines),
        }),
        "docs/agents/workflows.md": _fill("workflows.md.tmpl", {
            "distribution_source_text": source,
            "distribution_version_text": version,
            "selected_workflows": selected_guidance,
            "project_summary": _string(project_summary, "project_summary"),
            "documentation_policy": _string(documentation_policy, "documentation_policy"),
        }),
        "docs/agents/records.md": _fill("records.md.tmpl", {
            "route_rows": "\n".join(route_rows),
            "backend_assets": "\n".join(asset_lines),
        }),
    }
    section = _fill("agents-section.md.tmpl", {})
    files[root_guidance_path] = _managed_guidance(existing_root_guidance, section)
    for name in assets:
        files[f"docs/agents/backends/{name}"] = (BACKEND_DIR / name).read_bytes()
    return dict(sorted(files.items()))
