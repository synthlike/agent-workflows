#!/usr/bin/env python3
"""Validate immutable distribution identity in a workflow configuration."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


COMMIT_SHA = re.compile(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}")
SEMVER = re.compile(
    r"v?(?:0|[1-9][0-9]*)\."
    r"(?:0|[1-9][0-9]*)\."
    r"(?:0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)
PLACEHOLDER = re.compile(r"(?:REQUIRED|REPLACE|OWNER|EXAMPLE)", re.I)


def _scalar(value: str) -> str:
    value = value.split(" #", 1)[0].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value.strip()


def distribution_identity(text: str) -> tuple[str | None, str | None]:
    """Read direct scalar values from the top-level distribution mapping."""
    in_distribution = False
    values: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent == 0:
            in_distribution = line.strip() == "distribution:"
            continue
        if not in_distribution or indent < 2:
            continue
        match = re.match(r"^  (source|version):\s*(.*?)\s*$", line)
        if match:
            values[match.group(1)] = _scalar(match.group(2))
    return values.get("source"), values.get("version")


def validate(path: Path) -> list[str]:
    text = path.read_text()
    source, version = distribution_identity(text)
    errors: list[str] = []
    schema = re.search(r"(?m)^schema_version:\s*([0-9]+)\s*$", text)
    if not schema or schema.group(1) != "3":
        errors.append("schema_version must be 3")
    for obsolete in ("issue_tracker", "artifacts", "specifications"):
        if re.search(rf"(?m)^{obsolete}:\s*$", text):
            errors.append(f"obsolete schema field: {obsolete}")
    if not source:
        errors.append("missing distribution.source")
    elif PLACEHOLDER.search(source):
        errors.append("distribution.source is still a placeholder")

    if not version:
        errors.append("missing distribution.version")
    elif PLACEHOLDER.search(version):
        errors.append("distribution.version is still a placeholder")
    elif not (COMMIT_SHA.fullmatch(version) or SEMVER.fullmatch(version)):
        errors.append(
            "distribution.version must be an exact semantic release version "
            "or a 40/64-character commit SHA"
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="path to .agents/workflows.yaml")
    args = parser.parse_args()
    if not args.config.is_file():
        print(f"Workflow configuration not found: {args.config}", file=sys.stderr)
        return 1
    errors = validate(args.config)
    if errors:
        print(f"Invalid workflow configuration: {args.config}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Verified immutable distribution identity in {args.config}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
