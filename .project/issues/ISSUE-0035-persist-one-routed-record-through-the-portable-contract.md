---
id: ISSUE-0035
title: Persist one routed record through the portable contract
kind: task
status: resolved
created: 2026-08-25
assignee: pi
parent: ../../docs/specifications/record-routing-and-backend-contracts.md
blocked_by: []
labels: [record-routing, phase-1]
---

# Persist one routed record through the portable contract

## Question or work

Deliver a tracer path that creates, reads, searches, revision-updates, references, and archives a local Markdown `research` record through the backend-neutral contract.

## Acceptance criteria

- Shared request, response, revision, error, and structured-reference shapes are executable and tested.
- Create allocates identity within the operation.
- A stale revision fails without mutation.
- The conformance test seam can be reused by other adapters.
- Existing schema-2 consumers remain green during this expansion step.

## Parent

[Record routing and backend conformance](../../docs/specifications/record-routing-and-backend-contracts.md)

## Comments

## Resolution

Implemented the portable record request, response, error, revision, stored-record, and structured-reference shapes in `backends/record-store/contract.py`. Added a local Markdown `research` tracer with create-time identity allocation, complete reads, stable list/search, revision-gated atomic replacement, retained archive state, repository containment, lazy directories, and canonical JSON CLI output. Added a reusable adapter conformance mixin plus local destination, malformed-record, shape, and validation tests. A direct CLI create/read/update smoke check passed, and `scripts/verify.sh` passes with 56 tests while schema-2 consumers remain supported.
