#!/usr/bin/env python3
"""Verify the published workflow dependency table and report closures."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)+")
TABLE_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|$")
INLINE_CODE = re.compile(r"`([^`]+)`")


def skill_names(root: Path) -> set[str]:
    return {path.parent.name for path in (root / "skills").glob("*/SKILL.md")}


def declared_dependencies(root: Path, names: set[str]) -> dict[str, set[str]]:
    declared: dict[str, set[str]] = {}
    for name in sorted(names):
        text = (root / "skills" / name / "SKILL.md").read_text()
        declared[name] = {
            target
            for target in INLINE_CODE.findall(text)
            if target in names and target not in {name, "configure-workflows"}
        }
    return declared


def published_dependencies(path: Path) -> tuple[dict[str, set[str]], list[str]]:
    published: dict[str, set[str]] = {}
    errors: list[str] = []
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        match = TABLE_ROW.match(line)
        if not match:
            continue
        name, cell = match.groups()
        if not NAME.fullmatch(name):
            continue
        if name in published:
            errors.append(f"{path}:{line_number}: duplicate row for {name}")
            continue
        dependencies = set(INLINE_CODE.findall(cell))
        if cell.strip() != "None" and not dependencies:
            errors.append(f"{path}:{line_number}: dependencies for {name} are not skill names")
        published[name] = dependencies
    if not published:
        errors.append(f"{path}: no workflow dependency rows found")
    return published, errors


def validate(root: Path, table: Path) -> tuple[dict[str, set[str]], list[str]]:
    names = skill_names(root)
    published, errors = published_dependencies(table)
    if not names:
        errors.append(f"{root / 'skills'}: no skills found")
        return published, errors

    for missing in sorted(names - published.keys()):
        errors.append(f"dependency table is missing skill {missing}")
    for unknown in sorted(published.keys() - names):
        errors.append(f"dependency table names unknown skill {unknown}")
    for source, dependencies in sorted(published.items()):
        for unknown in sorted(dependencies - names):
            errors.append(f"{source} depends on unknown skill {unknown}")

    declared = declared_dependencies(root, names)
    for name in sorted(names & published.keys()):
        missing = declared[name] - published[name]
        extra = published[name] - declared[name]
        if missing:
            errors.append(
                f"{name} is missing declared dependencies: {', '.join(sorted(missing))}"
            )
        if extra:
            errors.append(
                f"{name} publishes undeclared dependencies: {', '.join(sorted(extra))}"
            )
    return published, errors


def closure(selected: set[str], dependencies: dict[str, set[str]]) -> set[str]:
    unknown = selected - dependencies.keys()
    if unknown:
        raise ValueError(f"unknown selected skills: {', '.join(sorted(unknown))}")
    result = {"configure-workflows", *selected}
    pending = list(result)
    while pending:
        name = pending.pop()
        if name not in dependencies:
            raise ValueError(f"dependency table has no row for {name}")
        for dependency in dependencies[name] - result:
            result.add(dependency)
            pending.append(dependency)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skills", nargs="*", help="selected skill names")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="distribution repository root",
    )
    parser.add_argument(
        "--table",
        type=Path,
        help="dependency table (defaults to docs/workflow-dependencies.md)",
    )
    args = parser.parse_args()
    table = args.table or args.root / "docs/workflow-dependencies.md"
    dependencies, errors = validate(args.root, table)
    if errors:
        print("Workflow dependency verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Verified dependency rows for {len(dependencies)} skills.")
    if args.skills:
        try:
            selected_closure = closure(set(args.skills), dependencies)
        except ValueError as error:
            print(f"Cannot calculate closure: {error}", file=sys.stderr)
            return 1
        print("Required skill closure:")
        for name in sorted(selected_closure):
            print(f"- {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
