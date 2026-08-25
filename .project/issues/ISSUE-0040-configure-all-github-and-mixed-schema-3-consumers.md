---
id: ISSUE-0040
title: Configure all-GitHub and mixed schema-3 consumers
kind: task
status: resolved
created: 2026-08-25
assignee: pi
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

Completed schema-3 configuration and installed verification for all-GitHub and mixed local/GitHub routing. GitHub instances now require exact `type`, `repository`, and `login` settings with `OWNER/REPO` validation; every GitHub route requires its matching `workflow:record:*` destination. `configure-workflows` now expands all-local, all-GitHub, and mixed profiles into twelve explicit routes, requires actual-identity and complete capability preflight before route recommendation or approval, preserves separately reviewed stale-safe label provisioning, and generates only the contract plus guidance/helper pairs for backend types used by routes. Added all-GitHub, mixed, unused-instance, malformed-identity, wrong-label, exact-asset, and source-checkout-free fixtures. Generated local and GitHub helpers render each other's structured references without provider access. `scripts/verify.sh` passes with 97 tests.
