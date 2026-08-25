---
id: ISSUE-0060
title: "Implement local Markdown migration operations"
kind: "implementation"
status: open
created: 2026-08-25
assignee: 
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

- [ ] Export enumerates active and retained historical records with exact revision-bound snapshots and complete portable issue/non-issue state.
- [ ] Import is idempotent, collision-safe, preserves non-issue IDs and exact content, and records canonical provenance where needed.
- [ ] Issue import/retirement preserves relationships, comments, labels, assignee meaning, terminal state, and destination mappings without rewriting source content.
- [ ] Non-issue retirement archives; active issue retirement cancels with a tombstone; terminal issues retain state and receive provenance.
- [ ] Repeated operations and stale revisions fail safely and satisfy shared migration conformance tests.

## Blocked by

Portable migration specification and capabilities.

## Out of scope

GitHub, Bear, configuration cutover, and workflow orchestration.

## Comments


## Resolution
