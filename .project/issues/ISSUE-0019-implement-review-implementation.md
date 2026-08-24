---
id: ISSUE-0019
title: Implement review-implementation
kind: task
status: open
created: 2026-08-24
assignee:
parent: ../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md
blocked_by:
  - ISSUE-0016-implement-investigate-failure.md
  - ISSUE-0017-implement-capture-regression.md
  - ISSUE-0018-implement-triage-issue.md
labels: [v0.3, skill]
---

# Implement review-implementation

## Parent

[v0.3 project-foundation and feedback workflows](../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md)

## What to build

Add a read-only workflow that reviews actual code, configuration, tests, documentation, and repository state against authoritative intent and returns an evidence-based conformance verdict.

## Acceptance criteria

- [ ] The skill establishes a bounded change set and reads its issue, specifications, accepted ARPs, project guidance, implementation, tests, documentation, and relevant repository state.
- [ ] Authority ordering keeps specifications, accepted ARPs, implementation issues, code, and tests distinct while treating RFC discussion as context.
- [ ] Findings are material, cite severity, authoritative expectation, concrete evidence, impact, and recommended disposition, and exclude undocumented style preferences.
- [ ] The result is exactly `Conforms`, `Conforms with follow-up`, or `Does not conform`, using the specification's thresholds.
- [ ] Review never edits implementation and requires approval before comments, status changes, or follow-up issues.
- [ ] Conforming, non-blocking-follow-up, non-conforming, ambiguous-scope, and empty-findings scenarios verify the contract.
- [ ] v0.3 release metadata, schema-2 source inventory, dependency documentation, generated manifest, and verification include the skill.
- [ ] All repository verification passes.

## Blocked by

- [Implement investigate-failure](ISSUE-0016-implement-investigate-failure.md)
- [Implement capture-regression](ISSUE-0017-implement-capture-regression.md)
- [Implement triage-issue](ISSUE-0018-implement-triage-issue.md)

## Out of scope

- Fixing implementation under review.
- Claiming that a conforming verdict proves no defects exist.
- Creating or resolving follow-up work without approval.
