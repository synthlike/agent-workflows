#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command="${BEARCLI:-/Applications/Bear.app/Contents/MacOS/bearcli}"
workspace="${BEAR_SMOKE_WORKSPACE:-}"

if [[ "${BEAR_CRUD_APPROVED:-}" != "YES" ]]; then
  printf 'Refusing live Bear mutation: set BEAR_CRUD_APPROVED=YES after reviewing the disposable workspace.\n' >&2
  exit 2
fi
if [[ ! -x "$command" || "$command" != /* ]]; then
  printf 'BEARCLI must name an absolute executable: %s\n' "$command" >&2
  exit 2
fi
if [[ "$workspace" != agent-workflows-smoke/* || "$workspace" == "agent-workflows-smoke/" ]]; then
  printf 'BEAR_SMOKE_WORKSPACE must be a unique child of agent-workflows-smoke/.\n' >&2
  exit 2
fi

python3 -B - "$root/backends/record-store/bear.py" "$command" "$workspace" <<'PY'
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile

helper, command, workspace = sys.argv[1:]
backend = "bear-smoke"
route = "research"
record_type = "research"
semantic_id = "smoke-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + f"-{os.getpid()}"
base = [
    sys.executable, "-B", helper,
    "--command", command,
    "--workspace", workspace,
    "--backend", backend,
    "--destination-tag", route,
    "--timeout", "15",
]


def invoke(arguments, *, expected=0):
    completed = subprocess.run(
        [*base, *arguments], text=True, capture_output=True, check=False
    )
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise SystemExit(
            f"non-JSON Bear response for {arguments[0]}: {completed.stdout!r}; "
            f"stderr={completed.stderr!r}"
        ) from error
    if completed.returncode != expected:
        raise SystemExit(
            f"Bear command {arguments[0]} returned {completed.returncode}, expected {expected}: {value}"
        )
    return value


# This is the only preflight invocation; it calls no Bear tool.
preflight = subprocess.run(
    [
        sys.executable, "-B", helper,
        "--command", command,
        "--workspace", workspace,
        "--timeout", "15", "preflight",
    ],
    text=True, capture_output=True, check=False,
)
if preflight.returncode:
    raise SystemExit(f"Bear preflight failed: {preflight.stdout} {preflight.stderr}")

with tempfile.TemporaryDirectory() as directory:
    temporary = Path(directory)
    initial = temporary / "initial.md"
    revised = temporary / "revised.md"
    initial.write_text("Initial approved live-smoke content.\n")
    revised.write_text("Revised approved live-smoke content.\n")

    created = invoke([
        "record-create", "--record-type", record_type,
        "--title", "Agent Workflows Bear smoke",
        "--content-file", str(initial), "--semantic-id", semantic_id,
    ])["record"]
    if created["id"] != semantic_id or created["content"] != initial.read_text():
        raise SystemExit("Bear create did not round-trip semantic identity and content")
    if created["metadata"]["archived"] is not False:
        raise SystemExit("Bear create unexpectedly archived the record")
    if not created["reference"]["href"].startswith("bear://x-callback-url/open-note?id="):
        raise SystemExit("Bear create returned an unexpected native reference")

    read = invoke(["record-read", "--record-type", record_type, semantic_id])["record"]
    if read != created:
        raise SystemExit("Bear read did not round-trip the created record")

    searched = invoke([
        "record-list", "--record-type", record_type, "--query", semantic_id,
    ])["records"]
    if [record["id"] for record in searched] != [semantic_id]:
        raise SystemExit("Bear search did not return exactly the smoke record")

    updated = invoke([
        "record-update", "--record-type", record_type, semantic_id,
        "--expected-revision", created["revision"],
        "--title", "Agent Workflows Bear smoke revised",
        "--content-file", str(revised),
    ])["record"]
    if updated["content"] != revised.read_text() or updated["revision"] == created["revision"]:
        raise SystemExit("Bear update did not return revised content and a new revision")

    stale = invoke([
        "record-update", "--record-type", record_type, semantic_id,
        "--expected-revision", created["revision"],
        "--content-file", str(initial),
    ], expected=1)
    if stale.get("error", {}).get("code") != "stale_revision":
        raise SystemExit(f"Bear stale-write check returned an unexpected error: {stale}")
    confirmed = invoke(["record-read", "--record-type", record_type, semantic_id])["record"]
    if confirmed != updated:
        raise SystemExit("Bear stale-write failure changed the record")

    archived = invoke([
        "record-archive", "--record-type", record_type, semantic_id,
        "--expected-revision", updated["revision"],
    ])["record"]
    if archived["metadata"]["archived"] is not True:
        raise SystemExit("Bear archive did not set managed archive metadata")
    remaining = invoke([
        "record-list", "--record-type", record_type, "--query", semantic_id,
    ])["records"]
    if remaining:
        raise SystemExit("metadata-archived Bear record remained in active search")

print(json.dumps({
    "cleanup": {
        "state": "metadata-archived",
        "native_note_retained": True,
        "record_id": semantic_id,
        "workspace_retained": workspace,
    },
    "ok": True,
    "operations": ["create", "read", "search", "update", "stale-update", "archive"],
}, sort_keys=True))
PY
