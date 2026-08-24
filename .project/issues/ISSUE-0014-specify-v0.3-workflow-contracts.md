---
id: ISSUE-0014
title: Specify the v0.3 workflow contracts
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent: ../../docs/rfcs/RFC-0004-focus-v0.3-on-project-feedback-workflows.md
blocked_by: []
labels: [v0.3, specification]
---

# Specify the v0.3 workflow contracts

## Parent

[RFC-0004: Focus v0.3 on project foundations and feedback workflows](../../docs/rfcs/RFC-0004-focus-v0.3-on-project-feedback-workflows.md)

## What to build

Turn the accepted v0.3 scope into an implementation-neutral specification for the six new skills, their authority and safety boundaries, release integration, and observable verification.

## Acceptance criteria

- [x] Each skill has a coherent trigger, inputs, process boundary, output, approval points, and failure behavior.
- [x] Artifact authority and project-owned location rules remain consistent with the existing artifact model.
- [x] Schema-2, harness-independence, vendored ownership, and manual-update boundaries are explicit.
- [x] Release integration and stable verification seams are specified.
- [x] The decision owner reviews and approves the specification.

## Blocked by

None.

## Out of scope

- Implementing skills or release integration.
- Reopening the accepted v0.3 roadmap decision.

## Comments

## Resolution

Resolved on 2026-08-24. The decision owner approved the [v0.3 project-foundation and feedback-workflows specification](../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md). It defines 84 requirements covering common authority and approval rules, all six skill contracts, schema-2 and manual-update continuity, release integration, and stable structural, scenario, dependency, distribution, and installed-adoption verification seams. There are no blocking open items.
