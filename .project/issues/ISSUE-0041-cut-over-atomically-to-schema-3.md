---
id: ISSUE-0041
title: Cut over atomically to schema 3
kind: task
status: resolved
created: 2026-08-25
assignee: pi
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

Cut the repository and distribution over atomically to schema 3. The root configuration, release metadata, generated manifest, all examples, fresh-install smoke setup, active documentation, root guidance, and generated consumer assets now use twelve explicit semantic routes and canonical `specs` / `docs/specs`. Installed and lightweight verification accept only schema 3 and reject old `issue_tracker`, `artifacts`, and `specifications` shapes. Removed the schema-2 reader, issue-tracker backend bridge, legacy bundled helpers/guidance, and generated `docs/agents/issue-tracker.md`; canonical backend sources and bundles now live only under `record-store`. Added `docs/agents/records.md` and exact local backend assets for this repository. Existing files under `docs/specifications` and all backend records/labels were left untouched; verification tests that existing records are not moved or rewritten. `scripts/verify.sh` passes with 100 tests.
