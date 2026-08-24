---
id: ISSUE-0013
title: Define the v0.3 scope
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent:
blocked_by: []
labels: [v0.3, rfc]
---

# Define the v0.3 scope

## What to build

Resolve whether v0.3 should implement the update lifecycle previously deferred by ARP-0004 or add workflows that improve technical project setup and the post-implementation feedback loop.

## Acceptance criteria

- [x] The RFC distinguishes requirements, constraints, preferences, non-goals, and assumptions.
- [x] The RFC defines the proposed responsibilities and boundaries of each new skill.
- [x] The RFC compares workflow-focused, update-focused, mixed, and no-change options.
- [x] The configuration-schema and manual-update boundaries are explicit.
- [x] The decision owner records an outcome.
- [x] Any accepted consequential roadmap decision is recorded as an ARP.

## Blocked by

None.

## Out of scope

- Implementing the selected v0.3 scope.
- Writing detailed skill contracts or implementation issues.

## Comments

## Resolution

Resolved on 2026-08-24. The decision owner accepted [RFC-0004](../../docs/rfcs/RFC-0004-focus-v0.3-on-project-feedback-workflows.md): v0.3 adds six project-foundation and feedback skills, retains schema 2 and reviewed manual updates, and provisionally defers transaction-safe update automation to v0.4. [ARP-0005](../../docs/decisions/ARP-0005-focus-v0.3-on-project-feedback-workflows.md) records the consequential roadmap decision. Detailed skill contracts and implementation planning remain separate work.
