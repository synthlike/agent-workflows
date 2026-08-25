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

record_source = root / "backends/record-store"
record_bundle = root / "skills/configure-workflows/references/backends/record-store"
for name in (
    "contract.py",
    "github.capabilities.json",
    "github.md",
    "github.py",
    "local-markdown.capabilities.json",
    "local-markdown.md",
    "local-markdown.py",
):
    source = root / "backends/record-store" / name
    bundled_copy = record_bundle / name
    if not bundled_copy.exists() or source.read_bytes() != bundled_copy.read_bytes():
        errors.append(f"{bundled_copy.relative_to(root)}: bundled record adapter is missing or stale")

for obsolete in (
    root / "backends/issue-tracker",
    root / "docs/agents/issue-tracker.md",
    root / "skills/configure-workflows/references/github-issues.py",
    root / "skills/configure-workflows/references/issue-tracker-contract.md",
    root / "skills/configure-workflows/references/issue-tracker-github.md",
    root / "skills/configure-workflows/references/issue-tracker-local-markdown.md",
):
    if obsolete.exists():
        errors.append(f"obsolete schema-2 asset remains: {obsolete.relative_to(root)}")

github_adapter = (root / "backends/record-store/github.md").read_text()
for label in (
    *(f"workflow:record:{name}" for name in ("issues", "domain", "arps", "rfcs", "specs", "meetings", "research", "questionnaires", "technical_baselines", "problem_framing", "prototypes", "handoffs")),
    *(f"workflow:issue:{name}" for name in ("initiative", "bug", "implementation", "clarification", "research", "prototype", "prerequisite")),
):
    if label not in github_adapter:
        errors.append(f"backends/record-store/github.md: missing managed label {label}")
for legacy in ("wayfinder:", "initiative:map", "initiative:task", "workflow:bug", "workflow:implementation"):
    if legacy in github_adapter:
        errors.append(f"backends/record-store/github.md: contains legacy label {legacy}")
for helper in (
    root / "backends/record-store/contract.py",
    root / "backends/record-store/github.py",
    root / "backends/record-store/local-markdown.py",
    record_bundle / "contract.py",
    record_bundle / "github.py",
    record_bundle / "local-markdown.py",
):
    try:
        compile(helper.read_text(), str(helper.relative_to(root)), "exec")
    except SyntaxError as error:
        errors.append(f"{helper.relative_to(root)}: invalid Python: {error}")

config_examples = [
    root / "skills/configure-workflows/references/workflow-config.example.yaml",
    root / "examples/github/workflows.yaml",
    root / "examples/local-markdown/workflows.yaml",
]
for path in config_examples:
    text = path.read_text()
    expected_schema = "schema_version: 3"
    for field in (
        expected_schema,
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
    for field in ("backends:", "records:", "issues:", "domain:", "arps:", "rfcs:", "specs:", "meetings:", "problem_framing:"):
        if field not in text:
            errors.append(f"{path.relative_to(root)}: missing schema-3 field {field.rstrip(':')}")
    if "backend: github" in text and "login:" not in text:
        errors.append(f"{path.relative_to(root)}: GitHub backend is missing login")

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
    "docs/record-backends.md",
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
print(f"Verified {len(skills)} skills, {len(list(record_source.glob('*.md'))) - 1} backends, {len(config_examples)} configuration examples, and {len(documentation)} documentation files.")
PY
python3 -B "$root/scripts/verify_workflow_config.py" "$root/.agents/workflows.yaml"
python3 -B "$root/scripts/verify_workflow_dependencies.py"
python3 -B "$root/skills/configure-workflows/references/lifecycle.py" \
  check-release --root "$root"
python3 -B "$root/skills/configure-workflows/references/lifecycle.py" \
  verify-consumer \
  --consumer-root "$root" \
  --skills-root "$root/skills"
python3 -B -m unittest discover -s "$root/tests" -p 'test_*.py'
bash -n "$root/scripts/smoke-fresh-install.sh"
node --check "$root/scripts/pi-discover-skills.mjs"
