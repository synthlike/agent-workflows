---
id: ISSUE-0016
title: Implement investigate-failure
kind: task
status: open
created: 2026-08-24
assignee:
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

- [ ] The skill distinguishes authoritative expected behavior from unconfirmed expectation and records observation, environment, scope, and reproduction.
- [ ] It inspects repository evidence, states competing hypotheses, and tests the cheapest discriminating evidence before reaching a conclusion.
- [ ] Disposable probes are disclosed and removed unless explicitly retained, and permanent fixes or opportunistic refactors are excluded.
- [ ] Findings identify evidence, falsified hypotheses, reproduction reliability, remaining uncertainty, and the smallest recommended next action.
- [ ] Issue writes and status changes require approval through the configured backend.
- [ ] Reproduced, disproved, non-reproducible, and probe-cleanup scenarios verify bounded conclusions and no permanent fix.
- [ ] v0.3 release metadata, schema-2 source inventory, dependency documentation, generated manifest, and verification include the skill.
- [ ] All repository verification passes.

## Blocked by

None.

## Out of scope

- Implementing a production fix.
- Encoding an unverified report as a regression test.
- Automatically changing issue status or creating follow-up work.
