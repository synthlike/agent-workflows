---
id: ISSUE-0042
title: Validate phase-1 backend conformance end to end
kind: task
status: open
created: 2026-08-25
assignee:
parent: ../../docs/specifications/record-routing-and-backend-contracts.md
blocked_by:
  - ISSUE-0041-cut-over-atomically-to-schema-3.md
labels: [record-routing, phase-1]
---

# Validate phase-1 backend conformance end to end

## Question or work

Establish release-ready evidence for local, GitHub, and mixed record routing.

## Acceptance criteria

- All-local, all-GitHub, and mixed installed-consumer scenarios pass.
- Disabled-route, stale-write, collision, malformed-reference, capability-rejection, and generated-helper integrity scenarios pass.
- Source-checkout-free lifecycle verification passes.
- Documentation describes actual behavior and limitations.
- The complete repository verification suite passes.

## Parent

[Record routing and backend conformance](../../docs/specifications/record-routing-and-backend-contracts.md)

## Comments

## Resolution
