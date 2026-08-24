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

config_examples = [
    root / "skills/configure-project/references/workflow-config.example.yaml",
    root / "examples/github/workflows.yaml",
    root / "examples/local-markdown/workflows.yaml",
]
for path in config_examples:
    text = path.read_text()
    for field in ("distribution:", "source:", "version:"):
        if field not in text:
            errors.append(f"{path.relative_to(root)}: missing {field.rstrip(':')}")
    if "REQUIRED_" in text and "Incomplete" not in text:
        errors.append(f"{path.relative_to(root)}: placeholders are not marked as incomplete")

if errors:
    print("Verification failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)
print(f"Verified {len(skills)} skills, {len(list((root / 'backends/issue-tracker').glob('*.md'))) - 1} backends, and {len(config_examples)} configuration examples.")
PY
python3 -B "$root/scripts/verify_workflow_config.py" "$root/.agents/workflows.yaml"
python3 -B "$root/scripts/verify_workflow_dependencies.py"
python3 -B -m unittest discover -s "$root/tests" -p 'test_*.py'
