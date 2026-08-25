---
id: ISSUE-0057
title: "Publish deterministic configuration as v0.6.0"
kind: "implementation"
status: cancelled
created: 2026-08-25
assignee: 
parent: "ISSUE-0050-streamline-deterministic-consumer-configuration.md"
blocked_by:
  - "ISSUE-0053-publish-the-complete-v0-5-0-release.md"
  - "ISSUE-0056-route-configure-workflows-through-plan-and-apply.md"
labels: ["lifecycle","configuration"]
---
# Publish deterministic configuration as v0.6.0

## Parent

Streamline deterministic consumer configuration

## What to build

Validate and publish the immutable release that makes consumer configuration deterministic and mechanically applicable.

## Acceptance criteria

- [ ] Release metadata advances from published v0.5.0 to exactly `v0.6.0` with a canonical regenerated manifest.
- [ ] Changelog and active documentation describe `plan-consumer`, `apply-consumer`, transactional caught-failure recovery, approval boundaries, and explicit exclusions.
- [ ] Complete repository verification, source-checkout-free plan/apply scenarios, fresh local smoke, and release integrity checks pass.
- [ ] A clean temporary consumer completes inspect, plan, approval simulation, apply, verify, and identical no-op replan without external backend invocation.
- [ ] After separate final publication approval, the release commit is tagged, pushed, and published as an immutable GitHub release.

## Blocked by

The configure-workflows plan/apply cutover and complete regressions.

## Out of scope

Skill updates, provider provisioning, schema migration, and backend-record migration.

## Comments
## Resolution

Superseded by the decision to publish all completed schema-3, Bear, discovery, canonical template, deterministic plan/apply, and strict cross-backend migration work together as the first immutable `v0.5.0` release under ISSUE-0053. No separate `v0.6.0` release remains planned for the already integrated deterministic configuration scope.
