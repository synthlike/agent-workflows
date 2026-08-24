#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
consumer="$(mktemp -d)"
cleanup() {
  if [[ "${KEEP_SMOKE_PROJECT:-}" == "1" ]]; then
    printf 'Retained smoke project: %s\n' "$consumer"
  else
    rm -rf "$consumer"
  fi
}
trap cleanup EXIT

git -C "$consumer" init -q
bundle="$consumer/agent-workflows-v0.3.0.tar.gz"
plan="$consumer/fresh-plan.json"
discovery="$consumer/pi-discovery.json"

python3 -B "$root/skills/configure-project/references/lifecycle.py" \
  build-bundle --root "$root" --output "$bundle"

(
  cd "$consumer"
  npx --yes skills@latest add "$root" \
    --skill configure-project develop-rfc \
    --agent pi \
    --copy \
    -y
)

command="$consumer/.pi/skills/configure-project/references/lifecycle.py"
test -f "$command"

python3 -B "$command" plan-fresh "$bundle" \
  --consumer-root "$consumer" \
  --skills-root "$consumer/.pi/skills" \
  --selected develop-rfc \
  --output "$plan" \
  --json >/dev/null

python3 -B "$command" apply-fresh "$bundle" \
  --consumer-root "$consumer" \
  --plan "$plan" \
  --json >/dev/null

pi_real="$(python3 -c 'import os, shutil; print(os.path.realpath(shutil.which("pi")))')"
pi_package_root="$(cd "$(dirname "$pi_real")/../.." && pwd)"
node "$root/scripts/pi-discover-skills.mjs" \
  "$pi_package_root/dist/index.js" \
  "$consumer" > "$discovery"

python3 -B - "$consumer" "$plan" "$discovery" <<'PY'
from pathlib import Path
import json
import sys

root = Path(sys.argv[1])
plan = json.loads(Path(sys.argv[2]).read_text())
discovery = json.loads(Path(sys.argv[3]).read_text())
if discovery["diagnostics"]:
    raise SystemExit("Pi discovery diagnostics: " + "; ".join(discovery["diagnostics"]))
discovered = {item["name"]: item["path"] for item in discovery["skills"]}
if set(discovered) != set(plan["required_installed"]):
    raise SystemExit(
        f"Pi discovered {sorted(discovered)}, expected {plan['required_installed']}"
    )
fragment = plan["configuration"]
selected = "\n".join(f"    - {name}" for name in fragment["installation"]["selected"])
skills = "\n".join(f"    {name}: {path}" for name, path in sorted(discovered.items()))
(root / ".agents").mkdir(exist_ok=True)
(root / ".agents/workflows.yaml").write_text(
    f"""schema_version: 2

distribution:
  source: {fragment['distribution']['source']}
  version: {fragment['distribution']['version']}

installation:
  selected:
{selected}
  skills:
{skills}

issue_tracker:
  backend: local-markdown
  root: .project

artifacts:
  domain: {{enabled: true, path: docs/domain}}
  arps: {{enabled: true, path: docs/decisions, prefix: ARP}}
  rfcs: {{enabled: true, path: docs/rfcs, prefix: RFC}}
  meetings: {{enabled: false, path: docs/meetings}}
  specifications: {{enabled: true, path: docs/specifications}}
"""
)
PY

mkdir -p "$consumer/docs/agents"
cp \
  "$consumer/.pi/skills/configure-project/references/issue-tracker-local-markdown.md" \
  "$consumer/docs/agents/issue-tracker.md"
cat > "$consumer/docs/agents/workflows.md" <<'MD'
# Engineering workflows

Canonical configuration is in [`.agents/workflows.yaml`](../../.agents/workflows.yaml). Issue operations follow [the configured backend](issue-tracker.md).

## Documentation style

Write clear, direct documentation. Prefer active voice, short sentences, explicit references, and established domain terms. Avoid idioms, unnecessary synonyms, and ambiguous pronouns. Use one action per procedural step.
MD
cat > "$consumer/AGENTS.md" <<'MD'
# Agent guidance

Workflow configuration is in `.agents/workflows.yaml`. Read `docs/agents/workflows.md` and `docs/agents/issue-tracker.md` before workflow operations.
MD

(
  cd /
  python3 -B "$command" verify-consumer \
    --consumer-root "$consumer" \
    --skills-root "$consumer/.pi/skills" \
    --json >/dev/null
)

for optional in \
  .project \
  docs/domain \
  docs/decisions \
  docs/rfcs \
  docs/meetings \
  docs/specifications
do
  if [[ -e "$consumer/$optional" ]]; then
    printf 'Optional path was created eagerly: %s\n' "$optional" >&2
    exit 1
  fi
done

printf 'Fresh-install smoke test passed with skills@latest and Pi.\n'
