#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command="${BEARCLI:-/Applications/Bear.app/Contents/MacOS/bearcli}"
workspace="${BEAR_WORKSPACE:-agent-workflows/preflight}"

if [[ ! -x "$command" ]]; then
  if [[ "${BEARCLI_REQUIRED:-0}" == "1" ]]; then
    printf 'Bear preflight required but executable is unavailable: %s\n' "$command" >&2
    exit 1
  fi
  python3 -B - "$command" <<'PY'
import json
import sys
print(json.dumps({
    "command": sys.argv[1],
    "ok": True,
    "reason": "bearcli unavailable",
    "skipped": True,
}, sort_keys=True))
PY
  exit 0
fi

python3 -B "$root/backends/record-store/bear.py" \
  --command "$command" \
  --workspace "$workspace" \
  preflight
