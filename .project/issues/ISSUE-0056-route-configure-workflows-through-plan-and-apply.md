---
id: ISSUE-0056
title: "Route configure-workflows through plan and apply"
kind: "implementation"
status: resolved
created: 2026-08-25
assignee: "pi"
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

Routed `configure-workflows` through the installed deterministic lifecycle. It now performs provider-neutral initial inspection, uses one project/profile sequence to gather only unresolved intent, conditionally obtains GitHub or read-only Bear evidence, normalizes strict answers, invokes `plan-consumer` instead of composing files, presents one complete digest-bound plan, and requests one approval for all local files before invoking `apply-consumer`. It forbids hand-authored repair, stops and replans on changed intent/state or any apply error, reports apply/verification results, and keeps GitHub label application separately planned and approved while Bear preflight remains read-only. Updated the authoritative configuration requirements and active README, fresh-project, existing-adoption, starting, and workflow-configuration guidance with the streamlined interaction and limitations. Replaced the fresh-install smoke's hand-authored YAML/Markdown/copy steps with source-checkout-free plan/apply, dynamic prior-state binding, manual-invocation Pi discovery checks, digest extraction, installed verification, and lazy destination assertions. Added regressions for the workflow sequence and smoke contract; prior lifecycle tests collectively cover deterministic plans, stale rejection, root preservation, verification, lazy destinations, local-only zero-provider invocation, source-checkout-free operation, rollback, and no-op replanning. `scripts/verify.sh` passes with 158 tests, and the live opt-in `scripts/smoke-fresh-install.sh` passes with `skills@latest` and Pi.
