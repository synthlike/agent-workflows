---
id: ISSUE-0016
title: Implement investigate-failure
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent: ../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md
blocked_by: []
labels: [v0.3, skill]
---

# Implement investigate-failure

## Parent

[v0.3 project-foundation and feedback workflows](../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md)

## What to build

Add a diagnosis-only workflow that reproduces unexpected behavior, tests competing hypotheses, and reports a supported root cause or bounded uncertainty without silently implementing a fix.

## Acceptance criteria

- [x] The skill distinguishes authoritative expected behavior from unconfirmed expectation and records observation, environment, scope, and reproduction.
- [x] It inspects repository evidence, states competing hypotheses, and tests the cheapest discriminating evidence before reaching a conclusion.
- [x] Disposable probes are disclosed and removed unless explicitly retained, and permanent fixes or opportunistic refactors are excluded.
- [x] Findings identify evidence, falsified hypotheses, reproduction reliability, remaining uncertainty, and the smallest recommended next action.
- [x] Issue writes and status changes require approval through the configured backend.
- [x] Reproduced, disproved, non-reproducible, and probe-cleanup scenarios verify bounded conclusions and no permanent fix.
- [x] v0.3 release metadata, schema-2 source inventory, dependency documentation, generated manifest, and verification include the skill.
- [x] All repository verification passes.

## Blocked by

None.

## Out of scope

- Implementing a production fix.
- Encoding an unverified report as a regression test.
- Automatically changing issue status or creating follow-up work.

## Comments

## Resolution

Resolved on 2026-08-24. `investigate-failure` now bounds expected and observed behavior, establishes reproduction, tests competing hypotheses with discriminating evidence, controls and cleans disposable probes, and reports either a supported root cause or bounded uncertainty. Its reusable findings template preserves evidence without turning diagnosis into repair, and issue publication requires approval. v0.3 metadata, schema-2 inventory, dependencies, and manifest include the skill. Three new contract scenarios and all 63 tests pass.
