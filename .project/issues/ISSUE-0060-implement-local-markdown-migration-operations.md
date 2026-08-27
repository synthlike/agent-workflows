---
id: ISSUE-0060
title: "Implement local Markdown migration operations"
kind: "implementation"
status: resolved
created: 2026-08-25
assignee: "pi"
parent: "ISSUE-0058-implement-strict-cross-backend-record-migration.md"
blocked_by:
  - "ISSUE-0059-specify-portable-migration-snapshots-and-capabilities.md"
labels: ["migration","local-markdown"]
---
# Implement local Markdown migration operations

## Parent

Implement strict cross-backend record migration

## What to build

Implement complete issue and non-issue migration export, import, semantic verification, collision handling, and retirement for local Markdown under the accepted migration contract.

## Acceptance criteria

- [x] Export enumerates active and retained historical records with exact revision-bound snapshots and complete portable issue/non-issue state.
- [x] Import is idempotent, collision-safe, preserves non-issue IDs and exact content, and records canonical provenance where needed.
- [x] Issue import/retirement preserves relationships, comments, labels, assignee meaning, terminal state, and destination mappings without rewriting source content.
- [x] Non-issue retirement archives; active issue retirement cancels with a tombstone; terminal issues retain state and receive provenance.
- [x] Repeated operations and stale revisions fail safely and satisfy shared migration conformance tests.

## Blocked by

Portable migration specification and capabilities.

## Out of scope

GitHub, Bear, configuration cutover, and workflow orchestration.

## Comments

### 2026-08-27T18:55:30Z — pi

ARP-0011 later externalized migration from the core distribution. This completed work remains historical evidence, but its implementation and active release claims were removed from v0.5.0. Git history retains the implementation for possible use by a separate optional migration project.

## Resolution

Implemented local Markdown migration export, lossless/idempotent import, semantic verification, collision handling, revision-gated retirement, durable provenance, and CLI access for issues and all non-issue record types. Added conformance coverage for exact content, relationships, comments, lifecycle state, replays, collisions, and stale writes. `scripts/verify.sh` passes with 176 tests.
