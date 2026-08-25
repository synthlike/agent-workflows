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
discovery="$consumer/pi-discovery.json"

(
  cd "$consumer"
  npx --yes skills@latest add "$root" \
    --skill '*' \
    --agent pi \
    --copy \
    -y
)

command="$consumer/.pi/skills/configure-workflows/references/lifecycle.py"
test -f "$command"

pi_real="$(python3 -c 'import os, shutil; print(os.path.realpath(shutil.which("pi")))')"
pi_package_root="$(cd "$(dirname "$pi_real")/../.." && pwd)"
node "$root/scripts/pi-discover-skills.mjs" \
  "$pi_package_root/dist/index.js" \
  "$consumer" > "$discovery"

python3 -B - "$consumer" "$discovery" <<'PY'
from pathlib import Path
import json
import sys

root = Path(sys.argv[1])
discovery = json.loads(Path(sys.argv[2]).read_text())
if discovery["diagnostics"]:
    raise SystemExit("Pi discovery diagnostics: " + "; ".join(discovery["diagnostics"]))
discovered = {item["name"]: item["path"] for item in discovery["skills"]}
manifest = json.loads(
    (root / ".pi/skills/configure-workflows/references/distribution-manifest.json").read_text()
)
expected = set(manifest["skills"])
if set(discovered) != expected:
    raise SystemExit(f"Pi discovered {sorted(discovered)}, expected {sorted(expected)}")
selected = "    - frame-product-problem"
skills = "\n".join(f"    {name}: {path}" for name, path in sorted(discovered.items()))
distribution = manifest["distribution"]
(root / ".agents").mkdir(exist_ok=True)
(root / ".agents/workflows.yaml").write_text(
    f"""schema_version: 3

distribution:
  source: {distribution['source']}
  version: {distribution['version']}

installation:
  selected:
{selected}
  skills:
{skills}

backends:
  local:
    type: local-markdown

records:
  issues:
    enabled: true
    backend: local
    destination: {{root: .project}}
  domain:
    enabled: true
    backend: local
    destination: {{path: docs/domain}}
  arps:
    enabled: true
    backend: local
    destination: {{path: docs/decisions, prefix: ARP}}
  rfcs:
    enabled: true
    backend: local
    destination: {{path: docs/rfcs, prefix: RFC}}
  specs:
    enabled: true
    backend: local
    destination: {{path: docs/specs}}
  meetings:
    enabled: false
    backend: local
    destination: {{path: docs/meetings}}
  research:
    enabled: true
    backend: local
    destination: {{path: docs/research}}
  questionnaires:
    enabled: true
    backend: local
    destination: {{path: docs/questionnaires}}
  technical_baselines:
    enabled: true
    backend: local
    destination: {{path: docs/engineering}}
  problem_framing:
    enabled: true
    backend: local
    destination: {{path: docs/product}}
  prototypes:
    enabled: false
    backend: local
    destination: {{path: docs/prototypes}}
  handoffs:
    enabled: false
    backend: local
    destination: {{path: .agents/handoffs}}
"""
)
PY

mkdir -p "$consumer/docs/agents/backends"
cp \
  "$consumer/.pi/skills/configure-workflows/references/backends/record-store/contract.py" \
  "$consumer/.pi/skills/configure-workflows/references/backends/record-store/local-markdown.md" \
  "$consumer/.pi/skills/configure-workflows/references/backends/record-store/local-markdown.py" \
  "$consumer/docs/agents/backends/"
cat > "$consumer/docs/agents/workflows.md" <<'MD'
# Engineering workflows

Canonical configuration is in [`.agents/workflows.yaml`](../../.agents/workflows.yaml). Record operations follow [the configured routes](records.md) in `docs/agents/records.md`.

## Documentation style

Write clear, direct documentation. Prefer active voice, short sentences, explicit references, and established domain terms. Avoid idioms, unnecessary synonyms, and ambiguous pronouns. Use one action per procedural step.
MD
cat > "$consumer/docs/agents/records.md" <<'MD'
# Record routing

Read `.agents/workflows.yaml`. Routes are `issues`, `domain`, `arps`, `rfcs`, `specs`, `meetings`, `research`, `questionnaires`, `technical_baselines`, `problem_framing`, `prototypes`, and `handoffs`.

Use `docs/agents/backends/local-markdown.py` for configured operations. Treat references and revisions as opaque. Mutations require approval; disabled routes prohibit persistence without new approval.
MD
cat > "$consumer/AGENTS.md" <<'MD'
# Agent guidance

Workflow configuration is in `.agents/workflows.yaml`. Read `docs/agents/workflows.md` and `docs/agents/records.md` before workflow operations.
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
  docs/specs \
  docs/research \
  docs/questionnaires \
  docs/engineering \
  docs/product \
  docs/prototypes \
  .agents/handoffs
do
  if [[ -e "$consumer/$optional" ]]; then
    printf 'Optional path was created eagerly: %s\n' "$optional" >&2
    exit 1
  fi
done

printf 'Complete-install smoke test passed with skills@latest and Pi.\n'
