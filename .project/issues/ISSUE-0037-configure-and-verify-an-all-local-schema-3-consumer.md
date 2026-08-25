---
id: ISSUE-0037
title: Configure and verify an all-local schema-3 consumer
kind: task
status: resolved
created: 2026-08-25
assignee: pi
parent: ../../docs/specifications/record-routing-and-backend-contracts.md
blocked_by:
  - ISSUE-0036-complete-the-local-markdown-reference-adapter.md
labels: [record-routing, phase-1]
---

# Configure and verify an all-local schema-3 consumer

## Question or work

Configure one schema-3 consumer with twelve explicit local routes and generated record and backend guidance.

## Acceptance criteria

- Schema-3 parsing rejects missing, extra, malformed, and unsupported fields.
- Profile questions expand to twelve explicit routes.
- `docs/agents/records.md` and local backend assets are generated.
- Disabled routes retain complete destinations.
- Installed lifecycle verification accepts the schema-3 fixture.
- Schema 2 remains temporarily readable only as an implementation bridge.

## Parent

[Record routing and backend conformance](../../docs/specifications/record-routing-and-backend-contracts.md)

## Comments

## Resolution

Added an all-local schema-3 configuration path with one named `local-markdown` backend and twelve explicit routes, including complete destinations on disabled routes and canonical `specs` / `docs/specs`. Installed lifecycle verification now strictly validates schema-3 top-level, backend, route, and destination fields; rejects missing, unknown, malformed, escaping, and unsupported values; verifies `docs/agents/records.md`; rejects obsolete issue guidance; and checks the exact generated local backend guidance, helper, and shared contract module. Bundled the local reference adapter with `configure-workflows`, updated the configuration interview and dry-run/write guidance, and added an installed schema-3 fixture that runs entirely from copied assets without creating record destinations. Schema 2 remains readable as the temporary implementation bridge and remains the repository's active schema until the atomic cutover. `scripts/verify.sh` passes with 69 tests.
