---
id: ARP-0005
title: Focus v0.3 on project foundations and feedback workflows
status: accepted
date: 2026-08-24
supersedes: []
superseded_by:
related_rfcs:
  - ../rfcs/RFC-0004-focus-v0.3-on-project-feedback-workflows.md
---

# Focus v0.3 on project foundations and feedback workflows

## Context

ARP-0004 deferred reusable update automation to v0.3 so the project could first ship a safe fresh-project lifecycle. With v0.2 complete, the more immediate workflow gaps are establishing an engineering foundation for an agreed technical stack and feeding implementation evidence back into executable work and initiative outcomes. There is still little evidence that update transactions are the highest-value next capability.

## Decision

v0.3 adds six semantic workflows:

- `establish-technical-baseline` establishes a minimal, production-compatible foundation for an already selected stack without inventing product architecture;
- `triage-issue` turns approved incoming reports into actionable issue scope or routes them to clarification and investigation;
- `investigate-failure` produces evidence and diagnosis without implementing a permanent fix;
- `capture-regression` encodes an accepted defect as a minimal durable check without changing production behavior;
- `review-implementation` performs read-only conformance review of actual implementation against issues, specifications, and accepted ARPs; and
- `close-initiative` verifies and records achieved, partial, or abandoned outcomes.

v0.3 retains configuration schema 2 and reviewed manual updates. It does not implement reusable update planning, replacement, rollback, recovery, migration, or lifecycle self-update. That work is provisionally deferred to v0.4 and may be reprioritized when adoption or demonstrated update pain warrants it.

This decision refines ARP-0004's roadmap expectation without changing its accepted v0.2 fresh-project boundary.

## Rationale

The new skills address recurring semantic operations while remaining independent of application stack and harness. Deferring update automation avoids shipping an integrity-sensitive partial solution before real v0.2 installations reveal compatibility and recovery needs. Keeping schema 2 prevents unrelated configuration churn.

## Consequences

- Detailed contracts, dependencies, tests, and documentation are required for six new skills.
- The technical baseline is a supporting index at a project-approved location; accepted decisions remain in ARPs and unresolved choices in RFCs.
- Investigation and review do not silently fix or mutate the work they assess.
- v0.3 consumers continue using installed verification and the reviewed manual update procedure.
- Update automation must be reconsidered when there are multiple active consumers, external adoption, repeated update failures, material local skill customization, or update effort blocks adoption.
- The next planned configuration schema remains schema 2.
