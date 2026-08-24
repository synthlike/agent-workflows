---
id: ISSUE-0004
title: Align installation and update guidance with the v0.1 contract
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent: ../../docs/specifications/v0.1-installation-and-consumer-project-contract.md
blocked_by:
  - ISSUE-0001-record-immutable-distribution-identity.md
  - ISSUE-0002-publish-and-verify-workflow-dependencies.md
labels: [v0.1, documentation]
---

# Align installation and update guidance with the v0.1 contract

## Parent

[v0.1 installation and consumer-project contract](../../docs/specifications/v0.1-installation-and-consumer-project-contract.md)

## What to build

Give new and existing consumers one consistent installation and update story that implements the accepted behavior-based contract and links to its authoritative specification.

## Acceptance criteria

- [x] README installation guidance requires `configure-project` plus the dependency closure of selected workflows.
- [x] Third-party installer commands are explicitly illustrative rather than guaranteed interfaces.
- [x] Documentation permits any harness-discoverable skill location and an equivalent intact manual copy.
- [x] Setup guidance explains one configuration per Git root, immutable source-version recording, approved dry runs, and lazy optional directories.
- [x] Adoption and update guidance clearly distinguish distribution-managed vendored files from consumer-owned configuration, guidance, backend state, local changes, and artifacts.
- [x] Update guidance requires reviewed diffs, preserved consumer files, surfaced local modifications, and no automatic migrations.
- [x] Documentation links the accepted RFC, ARP, specification, dependency table, and consumer verification entry point without duplicating their full content.
- [x] Link and structural verification passes.

## Blocked by

- [Record immutable distribution identity during project configuration](ISSUE-0001-record-immutable-distribution-identity.md)
- [Publish and verify the v0.1 workflow dependency table](ISSUE-0002-publish-and-verify-workflow-dependencies.md)

## Out of scope

Publishing a release, implementing an installer or updater, or migrating existing consumers.

## Comments

## Resolution

Resolved on 2026-08-24. README and new-project guidance now define dependency-closed, harness-independent installation followed by approved root configuration and verification. Existing-project and update guidance define the distribution/consumer ownership boundary, preserve consumer files, surface local skill changes, and prohibit automatic migrations. README links the accepted RFC, ARP, specification, dependency table, and verifier. Structural verification now checks relative documentation links and required v0.1 contract links; all 20 tests pass.
