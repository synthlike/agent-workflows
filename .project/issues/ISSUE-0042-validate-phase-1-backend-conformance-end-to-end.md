---
id: ISSUE-0042
title: "Validate phase-1 backend conformance end to end"
kind: "task"
status: resolved
created: 2026-08-25
assignee: "pi"
parent: "../../docs/specifications/record-routing-and-backend-contracts.md"
blocked_by:
  - "ISSUE-0041-cut-over-atomically-to-schema-3.md"
labels: ["record-routing","phase-1"]
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

Established release-ready phase-1 conformance evidence across all-local, all-GitHub, and mixed installed consumers. Installed verification now checks explicit backend capability declarations and rejects an `issues` route when any issue operation is absent before a backend write. End-to-end generated-helper checks cover valid and malformed cross-backend references in both directions, while disabled-route scenarios verify that configuration and installed guidance preserve approval boundaries without creating destinations. Existing shared suites continue to cover both adapters' complete record and issue contracts, stale writes, identifier collisions, lifecycle operations, and provider-specific behavior. Documented the deterministic mocked-GitHub boundary, workflow-level approval enforcement, local concurrency limits, and GitHub runtime dependencies. Source-checkout-free lifecycle verification and `scripts/verify.sh` pass with 101 tests.
