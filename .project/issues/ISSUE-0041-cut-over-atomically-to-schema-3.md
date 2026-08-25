---
id: ISSUE-0041
title: Cut over atomically to schema 3
kind: task
status: open
created: 2026-08-25
assignee:
parent: ../../docs/specifications/record-routing-and-backend-contracts.md
blocked_by:
  - ISSUE-0038-route-existing-workflows-through-record-adapters.md
  - ISSUE-0040-configure-all-github-and-mixed-schema-3-consumers.md
labels: [record-routing, phase-1]
---

# Cut over atomically to schema 3

## Question or work

Move the repository and distribution to schema 3 and remove the temporary schema-2 bridge.

## Acceptance criteria

- Schema-2 reading and obsolete issue-tracker guidance are removed.
- Repository configuration, examples, smoke setup, documentation, lifecycle assets, and release manifest use schema 3.
- `specifications` paths and keys become `specs`.
- Existing records and GitHub labels are not migrated.
- Verification rejects every schema-2 fixture.
- No compatibility aliases remain.

## Parent

[Record routing and backend conformance](../../docs/specifications/record-routing-and-backend-contracts.md)

## Comments

## Resolution
