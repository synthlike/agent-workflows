---
id: ISSUE-0020
title: Implement close-initiative
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent: ../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md
blocked_by:
  - ISSUE-0019-implement-review-implementation.md
labels: [v0.3, skill]
---

# Implement close-initiative

## Parent

[v0.3 project-foundation and feedback workflows](../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md)

## What to build

Add a workflow that verifies what an initiative delivered and records an honest achieved, partial, or abandoned outcome in existing initiative artifacts.

## Acceptance criteria

- [x] The skill identifies the original destination, success criteria, accepted scope changes, linked work, and authoritative specifications and decisions.
- [x] Delivered behavior and verification evidence, not resolved-issue counts, determine the proposed outcome.
- [x] Unresolved, blocked, cancelled, deferred, and unnecessary work are reconciled without presenting gaps as delivered.
- [x] The result is exactly `Achieved`, `Partially achieved`, or `Abandoned`, using the specification's thresholds.
- [x] Outcome, evidence, gaps, dispositions, follow-ups, and exact artifact changes receive approval before backend writes.
- [x] Closure updates the existing map or parent and creates approved follow-ups without introducing a canonical closure-report type.
- [x] Achieved, partial, and abandoned scenarios verify outcome evidence, artifact authority, and approval safety.
- [x] v0.3 release metadata, schema-2 source inventory, dependency documentation, generated manifest, and verification include the skill.
- [x] All repository verification passes.

## Blocked by

- [Implement review-implementation](ISSUE-0019-implement-review-implementation.md)

## Out of scope

- Inferring success from issue status alone.
- Automatically accepting incomplete delivery.
- Replacing specifications, ARPs, domain documentation, or issues with a closure report.

## Comments

## Resolution

Resolved on 2026-08-24. `close-initiative` now verifies the original destination and success criteria from delivered behavior and review evidence, reconciles unresolved and deferred work, and proposes exactly `Achieved`, `Partially achieved`, or `Abandoned`. Its reusable proposal requires approval before updating the existing map, parent, or issues and preserves lessons without creating a new authority type. The complete 19-skill v0.3 inventory, dependencies, manifest, and three new contract scenarios are verified; all 75 tests pass.
