#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
consumer="$(mktemp -d)"
answers="$(mktemp)"
plan="$(mktemp)"
cleanup() {
  rm -f "$answers" "$plan"
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

python3 -B - "$consumer" "$discovery" "$answers" <<'PY'
from pathlib import Path
import hashlib
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
manual = {
    name for name, entry in manifest["skills"].items()
    if entry["model_invocation"] == "manual"
}
if not manual or not manual <= set(discovered):
    raise SystemExit("Pi discovery omitted manual-invocation skills")
targets = {
    ".agents/workflows.yaml",
    "AGENTS.md",
    "docs/agents/workflows.md",
    "docs/agents/records.md",
    "docs/agents/backends/contract.py",
    "docs/agents/backends/local-markdown.md",
    "docs/agents/backends/local-markdown.py",
}
answer = {
    "answer_version": 1,
    "selection": {"mode": "explicit", "skills": ["frame-product-problem"]},
    "project": {
        "summary": "A fresh local project shared by people and coding agents.",
        "documentation_style": "Write clear, direct documentation with explicit references.",
    },
    "profile": {"name": "local-default", "local_backend": "local"},
    "backends": {"local": {"type": "local-markdown"}},
    "route_overrides": {},
    "consumer_state": {
        "root_guidance_path": "AGENTS.md",
        "expected_prior": {
            path: (
                "sha256:" + hashlib.sha256((root / path).read_bytes()).hexdigest()
                if (root / path).is_file() else None
            )
            for path in sorted(targets)
        },
    },
}
Path(sys.argv[3]).write_text(json.dumps(answer))
PY

(
  cd /
  python3 -B "$command" plan-consumer \
    --consumer-root "$consumer" \
    --skills-root "$consumer/.pi/skills" \
    --answers "$answers" > "$plan"
)
digest="$(python3 -B - "$plan" <<'PY'
from pathlib import Path
import json
import sys
print(json.loads(Path(sys.argv[1]).read_text())["digest"])
PY
)"
(
  cd /
  python3 -B "$command" apply-consumer \
    --consumer-root "$consumer" \
    --plan "$plan" \
    --expected-digest "$digest" >/dev/null
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
