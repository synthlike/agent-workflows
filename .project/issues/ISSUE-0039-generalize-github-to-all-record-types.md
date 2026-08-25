---
id: ISSUE-0039
title: Generalize GitHub to all record types
kind: task
status: resolved
created: 2026-08-25
assignee: pi
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

Generalized the GitHub Cloud helper into a portable record and issue adapter for all twelve semantic routes. Managed objects now use exactly one `workflow:record:*` label, with issue-routed objects additionally using exactly one `workflow:issue:*` kind; deterministic stale-safe label plans use schema 2. Non-issue records store semantic metadata and canonical content in managed issues, close as `completed` immediately after publication, search open and closed collections while excluding pull requests, preserve imported or allocated semantic IDs, archive without deletion, render structured references, and reject stale canonical updates after an immediate state recheck. The complete issue extension now exposes portable revisions and IDs while retaining explicit account/API identity verification, pagination, native sub-issues and dependencies, idempotent relationships, claim conflicts, frontier semantics, and distinct close reasons. Added portable CLI commands, complete shared record and issue conformance coverage, all-record label tests, external-change checks, canonical record-store assets, generated bundles, and updated guidance. `scripts/verify.sh` passes with 91 tests.
