#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 - "$root" <<'PY'
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
errors = []
skills = sorted((root / "skills").glob("*/SKILL.md"))
if not skills:
    errors.append("no skills found")

for path in skills:
    text = path.read_text()
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        errors.append(f"{path.relative_to(root)}: missing YAML frontmatter")
        continue
    frontmatter = match.group(1)
    name_match = re.search(r"^name:\s*([^\s]+)\s*$", frontmatter, re.M)
    description_match = re.search(r"^description:\s*(.+)$", frontmatter, re.M)
    if not name_match:
        errors.append(f"{path.relative_to(root)}: missing name")
        continue
    name = name_match.group(1)
    if name != path.parent.name:
        errors.append(f"{path.relative_to(root)}: name {name!r} does not match directory")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", name):
        errors.append(f"{path.relative_to(root)}: name must use verb-object kebab case")
    if not description_match or not description_match.group(1).strip():
        errors.append(f"{path.relative_to(root)}: missing description")
    for target in re.findall(r"\[[^]]*\]\(([^)]+)\)", text):
        if "://" in target or target.startswith("#"):
            continue
        resolved = (path.parent / target.split("#", 1)[0]).resolve()
        if not resolved.exists():
            errors.append(f"{path.relative_to(root)}: broken link {target}")

for forbidden in ("Monerium", "EMS", "CRUSH_", "docs/content/docs"):
    for path in list((root / "skills").rglob("*")) + list((root / "backends").rglob("*")):
        if path.is_file() and forbidden in path.read_text(errors="ignore"):
            errors.append(f"{path.relative_to(root)}: contains project-specific term {forbidden!r}")

contract = (root / "backends/issue-tracker/contract.md").read_text()
operations = re.findall(r"\d+\. \*\*([^:*]+)", contract)
for adapter in sorted((root / "backends/issue-tracker").glob("*.md")):
    if adapter.name == "contract.md":
        continue
    text = adapter.read_text().lower()
    for operation in operations:
        if operation.lower() not in text:
            errors.append(f"{adapter.relative_to(root)}: does not mention contract operation {operation}")

bundled = root / "skills/configure-project/references"
for source_name, bundled_name in (
    ("contract.md", "issue-tracker-contract.md"),
    ("github.md", "issue-tracker-github.md"),
    ("local-markdown.md", "issue-tracker-local-markdown.md"),
):
    source = root / "backends/issue-tracker" / source_name
    copy = bundled / bundled_name
    if not copy.exists() or source.read_text() != copy.read_text():
        errors.append(f"{copy.relative_to(root)}: bundled backend copy is missing or stale")

github_adapter = (root / "backends/issue-tracker/github.md").read_text()
for label in (
    "initiative:map",
    "initiative:research",
    "initiative:prototype",
    "initiative:clarification",
    "initiative:task",
):
    if f"`{label}`" not in github_adapter:
        errors.append(f"backends/issue-tracker/github.md: missing initiative label {label}")
if "wayfinder:" in github_adapter:
    errors.append("backends/issue-tracker/github.md: contains legacy wayfinder label namespace")

config_examples = [
    root / "skills/configure-project/references/workflow-config.example.yaml",
    root / "examples/github/workflows.yaml",
    root / "examples/local-markdown/workflows.yaml",
]
for path in config_examples:
    text = path.read_text()
    for field in (
        "schema_version: 2",
        "distribution:",
        "source:",
        "version:",
        "installation:",
        "selected:",
        "skills:",
        "research:",
        "questionnaires:",
        "technical_baselines:",
        "prototypes:",
        "handoffs:",
    ):
        if field not in text:
            errors.append(f"{path.relative_to(root)}: missing {field.rstrip(':')}")
    if "REQUIRED_" in text and "Incomplete" not in text:
        errors.append(f"{path.relative_to(root)}: placeholders are not marked as incomplete")

documentation = [root / "README.md", *(root / "docs").rglob("*.md"), *(root / ".project/issues").glob("*.md")]
for path in documentation:
    for target in re.findall(r"\[[^]]*\]\(([^)]+)\)", path.read_text()):
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("#"):
            continue
        resolved = (path.parent / target.split("#", 1)[0]).resolve()
        if not resolved.exists():
            errors.append(f"{path.relative_to(root)}: broken link {target}")

readme = (root / "README.md").read_text()
for required in (
    "docs/choosing-a-workflow.md",
    "docs/artifact-model.md",
    "docs/workflow-dependencies.md",
    "docs/distribution-manifest.md",
    "docs/workflow-configuration.md",
    "docs/verifying-installation.md",
    "docs/issue-tracker-backends.md",
    "docs/starting-a-new-project.md",
    "docs/fresh-project-configuration.md",
    "docs/adopting-in-existing-project.md",
):
    if f"]({required})" not in readme:
        errors.append(f"README.md: missing operational link {required}")

import json
metadata = json.loads((root / "release/metadata.json").read_text())
version = metadata["version"].removeprefix("v")
changelog = (root / "CHANGELOG.md").read_text()
unreleased = changelog.split("## Unreleased", 1)[-1].split("\n## ", 1)[0]
if f"## {version} " not in changelog and not re.search(r"(?m)^- ", unreleased):
    errors.append(
        "CHANGELOG.md: needs a dated current-release section or an Unreleased entry"
    )

if errors:
    print("Verification failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)
print(f"Verified {len(skills)} skills, {len(list((root / 'backends/issue-tracker').glob('*.md'))) - 1} backends, {len(config_examples)} configuration examples, and {len(documentation)} documentation files.")
PY
python3 -B "$root/scripts/verify_workflow_config.py" "$root/.agents/workflows.yaml"
python3 -B "$root/scripts/verify_workflow_dependencies.py"
python3 -B "$root/skills/configure-project/references/lifecycle.py" \
  check-release --root "$root"
python3 -B "$root/skills/configure-project/references/lifecycle.py" \
  verify-consumer \
  --consumer-root "$root" \
  --skills-root "$root/skills"
python3 -B -m unittest discover -s "$root/tests" -p 'test_*.py'
bash -n "$root/scripts/smoke-fresh-install.sh"
node --check "$root/scripts/pi-discover-skills.mjs"
