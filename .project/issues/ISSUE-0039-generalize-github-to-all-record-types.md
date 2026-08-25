---
id: ISSUE-0039
title: Generalize GitHub to all record types
kind: task
status: open
created: 2026-08-25
assignee:
parent: ../../docs/specifications/record-routing-and-backend-contracts.md
blocked_by:
  - ISSUE-0035-persist-one-routed-record-through-the-portable-contract.md
labels: [record-routing, phase-1]
---

# Generalize GitHub to all record types

## Question or work

Make GitHub conform for every record type while retaining the complete issue contract.

## Acceptance criteria

- GitHub passes the shared record conformance suite.
- Labels use `workflow:record:*` and `workflow:issue:*`.
- Non-issue records close as completed after publication.
- Canonical updates require matching revisions.
- Search covers open and closed records without treating pull requests as records.
- Existing identity, relationship, pagination, and close-reason behavior remains.

## Parent

[Record routing and backend conformance](../../docs/specifications/record-routing-and-backend-contracts.md)

## Comments

## Resolution
