---
id: ISSUE-0036
title: Complete the local Markdown reference adapter
kind: task
status: resolved
created: 2026-08-25
assignee: pi
parent: ../../docs/specifications/record-routing-and-backend-contracts.md
blocked_by:
  - ISSUE-0035-persist-one-routed-record-through-the-portable-contract.md
labels: [record-routing, phase-1]
---

# Complete the local Markdown reference adapter

## Question or work

Support all twelve record types and the complete issue extension through the local Markdown reference adapter.

## Acceptance criteria

- Every record operation passes the shared conformance suite.
- All issue operations retain current behavior.
- Paths remain repository-contained and directories are created lazily.
- Prefix allocation, collisions, malformed records, references, relationships, and frontier behavior are covered.
- Non-atomic concurrency limitations remain explicit.

## Parent

[Record routing and backend conformance](../../docs/specifications/record-routing-and-backend-contracts.md)

## Comments

## Resolution

Expanded the local Markdown adapter across all twelve routed record types. Eleven document-like types support create, read, stable list/search, guarded update, retained archive, legacy plain-Markdown reads, repository containment, and type-aware slug or ARP/RFC prefix allocation. The `issues` route implements guarded create, read, list, update, chronological comments, conflict-aware claims, resolve, cancel, parent, blocker, and deterministic frontier operations while reading the established local issue format. Relationship cycles and broken targets fail explicitly. Same-working-tree writes use cross-platform process locks and exact-byte revisions; unsynchronized working trees remain non-atomic. Added reusable issue conformance tests, all-record coverage, legacy record and issue fixtures, malformed and broken-reference checks, concurrent allocation checks, documentation, and CLI smoke coverage. `scripts/verify.sh` passes with 66 tests.
