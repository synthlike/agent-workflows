---
id: ISSUE-0040
title: Configure all-GitHub and mixed schema-3 consumers
kind: task
status: open
created: 2026-08-25
assignee:
parent: ../../docs/specifications/record-routing-and-backend-contracts.md
blocked_by:
  - ISSUE-0037-configure-and-verify-an-all-local-schema-3-consumer.md
  - ISSUE-0039-generalize-github-to-all-record-types.md
labels: [record-routing, phase-1]
---

# Configure all-GitHub and mixed schema-3 consumers

## Question or work

Complete configuration and verification for all-GitHub and mixed local/GitHub record routing.

## Acceptance criteria

- GitHub backend instances require explicit repository and login.
- Capability and identity preflight precede route approval.
- Label provisioning remains reviewed and stale-safe.
- Generated assets include exactly the backend types used.
- All-GitHub and mixed fixtures pass installed verification.
- Cross-backend references render correctly in both directions.

## Parent

[Record routing and backend conformance](../../docs/specifications/record-routing-and-backend-contracts.md)

## Comments

## Resolution
