---
id: ISSUE-0017
title: Implement capture-regression
kind: task
status: open
created: 2026-08-24
assignee:
parent: ../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md
blocked_by:
  - ISSUE-0016-implement-investigate-failure.md
labels: [v0.3, skill]
---

# Implement capture-regression

## Parent

[v0.3 project-foundation and feedback workflows](../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md)

## What to build

Add a workflow that encodes an accepted, reproducible defect as the smallest durable automated check without changing production behavior.

## Acceptance criteria

- [ ] The skill requires an established defect and routes speculative or unreproduced behavior back to investigation.
- [ ] It selects the narrowest stable test seam from project conventions and obtains approval for files, fixtures, command, and expected failure before writing.
- [ ] The new check is demonstrated to fail before the fix for the diagnosed reason rather than unrelated setup or environment failure.
- [ ] Production files, unrelated tests, external-service stability, and consumer-owned changes are preserved.
- [ ] Completion reports changed test files, the narrow command, failing result, and protected issue without committing automatically.
- [ ] Diagnosed, unconfirmed, red-commit-policy, and impractical-automation scenarios verify the contract.
- [ ] v0.3 release metadata, schema-2 source inventory, dependency documentation, generated manifest, and verification include the skill.
- [ ] All repository verification passes.

## Blocked by

- [Implement investigate-failure](ISSUE-0016-implement-investigate-failure.md)

## Out of scope

- Diagnosing the underlying failure.
- Implementing the production fix.
- Requiring a standalone commit containing a failing test.
