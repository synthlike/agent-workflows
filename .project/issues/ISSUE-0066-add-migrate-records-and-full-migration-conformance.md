---
id: ISSUE-0066
title: "Add migrate-records and full migration conformance"
kind: "implementation"
status: cancelled
created: 2026-08-25
assignee: 
parent: "ISSUE-0058-implement-strict-cross-backend-record-migration.md"
blocked_by:
  - "ISSUE-0065-cut-over-migrated-routes-and-retire-sources-safely.md"
labels: ["migration","workflow"]
---
# Add migrate-records and full migration conformance

## Parent

Implement strict cross-backend record migration

## What to build

Ship the manually invoked `migrate-records` skill, assisted invocation guidance, complete pairwise conformance, source-checkout-free lifecycle integration, and release-ready migration documentation.

## Acceptance criteria

- [ ] `migrate-records` uses lowercase verb-object naming, sets `disable-model-invocation: true`, and guides natural-language requests to explicit `/skill:migrate-records` invocation.
- [ ] The skill inspects configured routes/provider facts, asks only unresolved intent, explains cooperative freeze/non-atomic recovery, and presents exact copy, cutover, cleanup, and retirement approvals.
- [ ] It always uses migration plan/journal commands and configuration plan/apply rather than hand-authoring records, journals, configuration, or guidance.
- [ ] Installed local↔GitHub issue scenarios and all six non-issue directions among local/GitHub/Bear cover active/history fidelity, mappings, relationships, resume, collisions, stale state, freeze violations, cutover, roll-forward retirement, and no-op completion.
- [ ] Normal tests mock providers and perform no live mutation; optional external checks remain separately approved.
- [ ] Manifest, dependency inventory, templates/guidance, examples, smoke tests, active documentation, and v0.5 release notes include the complete skill and limitations.
- [ ] The complete repository and source-checkout-free verification suites pass.

## Blocked by

Safe cutover and source retirement.

## Out of scope

Model-invoked migration, reclassification, free-form link rewriting, deletion, Things, and implicit migration during configuration.

## Comments
## Resolution

Cancelled in the core repository after ARP-0011 externalized record migration as a possible separate optional project. The implementation is not part of v0.5.0 or assigned to a later core release. Historical commits and issue context are retained for future reference.
