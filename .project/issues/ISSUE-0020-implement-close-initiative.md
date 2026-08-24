---
id: ISSUE-0020
title: Implement close-initiative
kind: task
status: open
created: 2026-08-24
assignee:
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

- [ ] The skill identifies the original destination, success criteria, accepted scope changes, linked work, and authoritative specifications and decisions.
- [ ] Delivered behavior and verification evidence, not resolved-issue counts, determine the proposed outcome.
- [ ] Unresolved, blocked, cancelled, deferred, and unnecessary work are reconciled without presenting gaps as delivered.
- [ ] The result is exactly `Achieved`, `Partially achieved`, or `Abandoned`, using the specification's thresholds.
- [ ] Outcome, evidence, gaps, dispositions, follow-ups, and exact artifact changes receive approval before backend writes.
- [ ] Closure updates the existing map or parent and creates approved follow-ups without introducing a canonical closure-report type.
- [ ] Achieved, partial, and abandoned scenarios verify outcome evidence, artifact authority, and approval safety.
- [ ] v0.3 release metadata, schema-2 source inventory, dependency documentation, generated manifest, and verification include the skill.
- [ ] All repository verification passes.

## Blocked by

- [Implement review-implementation](ISSUE-0019-implement-review-implementation.md)

## Out of scope

- Inferring success from issue status alone.
- Automatically accepting incomplete delivery.
- Replacing specifications, ARPs, domain documentation, or issues with a closure report.
