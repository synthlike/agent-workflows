---
id: ISSUE-0065
title: "Cut over migrated routes and retire sources safely"
kind: "implementation"
status: open
created: 2026-08-25
assignee: 
parent: "ISSUE-0058-implement-strict-cross-backend-record-migration.md"
blocked_by:
  - "ISSUE-0064-copy-and-verify-migration-destinations-resumably.md"
labels: ["migration","configuration"]
---
# Cut over migrated routes and retire sources safely

## Parent

Implement strict cross-backend record migration

## What to build

Complete separately approved route cutover through deterministic configuration apply, then roll forward through verified source tombstones/archives with resumable recovery.

## Acceptance criteria

- [ ] Cutover requires complete destination verification, an acknowledged cooperative freeze, and a fresh revision/collision recheck of the entire source and destination inventories.
- [ ] The journal binds a canonical `configure-workflows` plan digest that changes only the selected route/backend assets and preserves all unrelated consumer bytes.
- [ ] Cutover invokes normal `apply-consumer`, records installed verification, and never edits configuration/guidance manually.
- [ ] After successful cutover, resume always rolls forward and never reverts the authoritative route.
- [ ] Retirement uses metadata archive for non-issues, cancellation tombstones for active issues, and provenance comments without terminal-state change for terminal issues.
- [ ] Every retirement is revision-gated, destination-linked, verified, and journaled; partial failure resumes idempotently.
- [ ] Final verification proves destination authority, complete mappings, source retirement, lazy paths, and no unplanned mutation.

## Blocked by

Verified resumable destination copy.

## Out of scope

Source deletion, post-cutover rollback, and provider provisioning without separate approval.

## Comments


## Resolution
