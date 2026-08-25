---
id: ISSUE-0056
title: "Route configure-workflows through plan and apply"
kind: "implementation"
status: open
created: 2026-08-25
assignee: 
parent: "ISSUE-0050-streamline-deterministic-consumer-configuration.md"
blocked_by:
  - "ISSUE-0055-apply-approved-consumer-configuration-plans-transactionally.md"
labels: ["lifecycle","configuration"]
---
# Route configure-workflows through plan and apply

## Parent

Streamline deterministic consumer configuration

## What to build

Replace hand-authored local setup with inspect, one project/profile question sequence, deterministic plan review, one approval, mechanical apply, and installed verification.

## Acceptance criteria

- [ ] `configure-workflows` uses initial inspection, gathers only unresolved project/profile intent, normalizes answers, and invokes `plan-consumer` rather than composing configuration or guidance manually.
- [ ] Local setup presents one complete plan and requests one approval before `apply-consumer`.
- [ ] GitHub identity/preflight and label planning occur only when GitHub is considered; label application remains separately approved.
- [ ] Bear executable/workspace preflight occurs only when Bear is considered and remains read-only.
- [ ] Regression tests cover manual-invocation Pi skills, deterministic plans, stale apply rejection, root-guidance preservation, generated verification, lazy disabled/unused destinations, no external tools for local-only setup, source-checkout-free operation, rollback, and no-op replanning.
- [ ] Fresh-project smoke uses the lifecycle plan/apply commands and requires no hand-authored repair.
- [ ] Documentation describes the streamlined interaction and remaining limitations accurately.
- [ ] The complete repository verification suite passes.

## Blocked by

Transactional consumer plan application.

## Out of scope

Provider mutations inside apply, skill installation or updates, and configuration-schema migration.

## Comments


## Resolution
