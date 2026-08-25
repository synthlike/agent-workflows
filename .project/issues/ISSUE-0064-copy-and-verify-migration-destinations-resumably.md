---
id: ISSUE-0064
title: "Copy and verify migration destinations resumably"
kind: "implementation"
status: open
created: 2026-08-25
assignee: 
parent: "ISSUE-0058-implement-strict-cross-backend-record-migration.md"
blocked_by:
  - "ISSUE-0060-implement-local-markdown-migration-operations.md"
  - "ISSUE-0061-implement-github-migration-operations.md"
  - "ISSUE-0062-implement-bear-migration-operations.md"
  - "ISSUE-0063-generate-migration-plans-and-resumable-journals.md"
labels: ["migration","lifecycle"]
---
# Copy and verify migration destinations resumably

## Parent

Implement strict cross-backend record migration

## What to build

Mechanically apply the separately approved destination-copy stage from a migration plan, verify semantic fidelity, and checkpoint every idempotent operation without changing authority.

## Acceptance criteria

- [ ] Apply requires the exact plan/journal digest and rechecks source revisions, destination state, provider identity, capabilities, containment, and cooperative freeze before writes.
- [ ] Records are imported in deterministic dependency order with exact content, canonical provenance, stable non-issue IDs, mapped issue references, comments, and structured relationships.
- [ ] Every successful destination mutation is immediately exported and semantically compared before its journal checkpoint.
- [ ] Caught or interrupted partial failure resumes without duplicates; pre-cutover cleanup is only separately planned and approved.
- [ ] The source route remains authoritative and configuration/source records remain unchanged throughout this stage.
- [ ] Full mocked pairwise conformance covers retries, stale state, collisions, unsupported fidelity, and no-op resume.

## Blocked by

All three adapter migration implementations and migration planning/journaling.

## Out of scope

Route cutover, source retirement, and automatic cleanup.

## Comments


## Resolution
