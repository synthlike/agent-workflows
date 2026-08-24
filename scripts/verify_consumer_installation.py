#!/usr/bin/env python3
"""Verify a configured consumer project and its harness-discoverable skills."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import Any

from verify_workflow_config import validate as validate_identity
from verify_workflow_dependencies import published_dependencies


FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
MARKDOWN_LINK = re.compile(r"\[[^]]*\]\(([^)]+)\)")
SKILL_NAME = re.compile(r"^name:\s*([^\s]+)\s*$", re.M)


def _strip_comment(value: str) -> str:
    quote: str | None = None
    for index, character in enumerate(value):
        if character in "\"'":
            quote = None if quote == character else character if quote is None else quote
        elif character == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.strip()


def _scalar(value: str) -> Any:
    value = _strip_comment(value.strip())
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if value == "true":
        return True
    if value == "false":
        return False
    if re.fullmatch(r"[0-9]+", value):
        return int(value)
    return value


def parse_config(text: str) -> dict[str, Any]:
    """Parse the mapping-only YAML subset used by workflows.yaml."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if "\t" in raw_line[: len(raw_line) - len(raw_line.lstrip())]:
            raise ValueError(f"line {line_number}: tabs are not valid indentation")
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            raise ValueError(f"line {line_number}: expected a mapping entry")
        key, value = (part.strip() for part in line.split(":", 1))
        if not key:
            raise ValueError(f"line {line_number}: empty mapping key")
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if key in parent:
            raise ValueError(f"line {line_number}: duplicate key {key}")
        if not value:
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        elif value.startswith("{") and value.endswith("}"):
            child = {}
            content = value[1:-1].strip()
            if content:
                for entry in content.split(","):
                    if ":" not in entry:
                        raise ValueError(f"line {line_number}: invalid inline mapping")
                    child_key, child_value = (part.strip() for part in entry.split(":", 1))
                    child[child_key] = _scalar(child_value)
            parent[key] = child
        else:
            parent[key] = _scalar(value)
    return root


def _contained_path(root: Path, value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be a non-empty repository-relative path")
        return
    path = Path(value)
    if path.is_absolute():
        errors.append(f"{label} must be repository-relative: {value}")
        return
    resolved_root = root.resolve()
    try:
        (resolved_root / path).resolve().relative_to(resolved_root)
    except ValueError:
        errors.append(f"{label} escapes the consumer root: {value}")


def validate_configuration(root: Path) -> list[str]:
    errors: list[str] = []
    config = root / ".agents/workflows.yaml"
    found = [
        path
        for path in root.rglob("workflows.yaml")
        if path.parent.name == ".agents" and ".git" not in path.relative_to(root).parts
    ]
    if config not in found:
        errors.append("missing root .agents/workflows.yaml")
    for nested in sorted(set(found) - {config}):
        errors.append(f"nested workflow configuration is not supported: {nested.relative_to(root)}")
    if not config.is_file():
        return errors

    try:
        data = parse_config(config.read_text())
    except ValueError as error:
        errors.append(f"invalid .agents/workflows.yaml: {error}")
        return errors

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    errors.extend(validate_identity(config))

    tracker = data.get("issue_tracker")
    if not isinstance(tracker, dict) or not isinstance(tracker.get("backend"), str):
        errors.append("issue_tracker.backend is required")
    elif tracker["backend"] == "local-markdown":
        _contained_path(root, tracker.get("root"), "issue_tracker.root", errors)

    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict) or not artifacts:
        errors.append("artifacts must define configured capabilities")
    else:
        for name, settings in artifacts.items():
            label = f"artifacts.{name}"
            if not isinstance(settings, dict):
                errors.append(f"{label} must be a mapping")
                continue
            if not isinstance(settings.get("enabled"), bool):
                errors.append(f"{label}.enabled must be true or false")
            _contained_path(root, settings.get("path"), f"{label}.path", errors)
            if name in {"arps", "rfcs"} and settings.get("enabled") is True:
                if not isinstance(settings.get("prefix"), str) or not settings["prefix"]:
                    errors.append(f"{label}.prefix is required when enabled")

    for guidance in (Path("docs/agents/workflows.md"), Path("docs/agents/issue-tracker.md")):
        path = root / guidance
        if not path.is_file() or not path.read_text().strip():
            errors.append(f"missing required guidance: {guidance}")

    guidance_files = [root / name for name in ("AGENTS.md", "CLAUDE.md") if (root / name).is_file()]
    if not any(
        ".agents/workflows.yaml" in path.read_text()
        and "docs/agents/workflows.md" in path.read_text()
        and "docs/agents/issue-tracker.md" in path.read_text()
        for path in guidance_files
    ):
        errors.append("root agent guidance must point to workflow and issue-backend guidance")
    return errors


def _tree(path: Path) -> dict[Path, bytes]:
    return {
        file.relative_to(path): file.read_bytes()
        for file in path.rglob("*")
        if file.is_file() and "__pycache__" not in file.parts
    }


def validate_skills(
    skill_dirs: list[Path], source_skills: Path, dependencies: dict[str, set[str]]
) -> list[str]:
    errors: list[str] = []
    installed: dict[str, Path] = {}
    for directory in skill_dirs:
        directory = directory.resolve()
        skill_file = directory / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"installed skill has no SKILL.md: {directory}")
            continue
        match = FRONTMATTER.match(skill_file.read_text())
        name_match = SKILL_NAME.search(match.group(1)) if match else None
        if not match or not name_match:
            errors.append(f"installed skill has no frontmatter name: {skill_file}")
            continue
        name = name_match.group(1)
        if name != directory.name:
            errors.append(f"installed skill name {name!r} does not match directory {directory.name!r}")
        if name in installed:
            errors.append(f"installed skill is duplicated: {name}")
            continue
        installed[name] = directory
        for target in MARKDOWN_LINK.findall(skill_file.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            relative = target.split("#", 1)[0]
            resolved = (directory / relative).resolve()
            try:
                resolved.relative_to(directory)
            except ValueError:
                errors.append(f"{name} reference escapes its skill directory: {target}")
                continue
            if not resolved.exists():
                errors.append(f"{name} has a broken relative reference: {target}")

        source = source_skills / name
        if not source.is_dir():
            errors.append(f"installed skill is absent from the distribution source: {name}")
        elif source.resolve() != directory:
            installed_tree = _tree(directory)
            source_tree = _tree(source)
            for path in sorted(source_tree.keys() - installed_tree.keys()):
                errors.append(f"{name} is missing distributed file: {path}")
            for path in sorted(installed_tree.keys() - source_tree.keys()):
                errors.append(f"{name} has locally added file: {path}")
            for path in sorted(installed_tree.keys() & source_tree.keys()):
                if installed_tree[path] != source_tree[path]:
                    errors.append(f"{name} has locally modified file: {path}")

    names = set(installed)
    if "configure-project" not in names:
        errors.append("installed skill set is missing required configure-project")
    for name in sorted(names):
        if name not in dependencies:
            errors.append(f"dependency table has no row for installed skill {name}")
            continue
        missing = dependencies[name] - names
        if missing:
            errors.append(f"{name} is missing installed dependencies: {', '.join(sorted(missing))}")
    return errors


def verify(
    consumer_root: Path,
    skill_dirs: list[Path],
    source_skills: Path,
    dependency_table: Path,
) -> list[str]:
    dependencies, errors = published_dependencies(dependency_table)
    errors.extend(validate_configuration(consumer_root.resolve()))
    errors.extend(validate_skills(skill_dirs, source_skills.resolve(), dependencies))
    return errors


def main() -> int:
    distribution_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consumer-root", required=True, type=Path)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--skills-root",
        type=Path,
        help="directory whose immediate child directories are discovered skills",
    )
    selection.add_argument(
        "--skill-dir",
        action="append",
        type=Path,
        help="one harness-discoverable skill directory; repeat for each skill",
    )
    parser.add_argument(
        "--source-skills",
        type=Path,
        default=distribution_root / "skills",
        help="unmodified distribution skill directories",
    )
    parser.add_argument(
        "--dependency-table",
        type=Path,
        default=distribution_root / "docs/workflow-dependencies.md",
    )
    args = parser.parse_args()
    if not args.consumer_root.is_dir():
        print(f"Consumer root not found: {args.consumer_root}", file=sys.stderr)
        return 1
    if args.skills_root:
        skill_dirs = sorted(path for path in args.skills_root.iterdir() if path.is_dir())
    else:
        skill_dirs = args.skill_dir
    errors = verify(args.consumer_root, skill_dirs, args.source_skills, args.dependency_table)
    if errors:
        print("Consumer installation verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Verified consumer installation with {len(skill_dirs)} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
