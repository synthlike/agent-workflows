---
id: ISSUE-0017
title: Implement capture-regression
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
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

- [x] The skill requires an established defect and routes speculative or unreproduced behavior back to investigation.
- [x] It selects the narrowest stable test seam from project conventions and obtains approval for files, fixtures, command, and expected failure before writing.
- [x] The new check is demonstrated to fail before the fix for the diagnosed reason rather than unrelated setup or environment failure.
- [x] Production files, unrelated tests, external-service stability, and consumer-owned changes are preserved.
- [x] Completion reports changed test files, the narrow command, failing result, and protected issue without committing automatically.
- [x] Diagnosed, unconfirmed, red-commit-policy, and impractical-automation scenarios verify the contract.
- [x] v0.3 release metadata, schema-2 source inventory, dependency documentation, generated manifest, and verification include the skill.
- [x] All repository verification passes.

## Blocked by

- [Implement investigate-failure](ISSUE-0016-implement-investigate-failure.md)

## Out of scope

- Diagnosing the underlying failure.
- Implementing the production fix.
- Requiring a standalone commit containing a failing test.

## Comments

## Resolution

Resolved on 2026-08-24. `capture-regression` now requires an established defect, selects and proposes the narrowest stable test seam, writes only approved test and fixture files, proves the pre-fix failure occurs for the diagnosed reason, and reports an exact handoff without committing or changing production behavior. It handles unconfirmed reports, impractical automation, and red-commit policies explicitly. v0.3 inventory, cyclic diagnosis/regression dependencies, manifest, and three new contract scenarios are verified; all 66 tests pass.
