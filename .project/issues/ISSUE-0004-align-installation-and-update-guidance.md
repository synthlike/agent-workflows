---
id: ISSUE-0004
title: Align installation and update guidance with the v0.1 contract
kind: task
status: open
created: 2026-08-24
assignee:
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

- [ ] README installation guidance requires `configure-project` plus the dependency closure of selected workflows.
- [ ] Third-party installer commands are explicitly illustrative rather than guaranteed interfaces.
- [ ] Documentation permits any harness-discoverable skill location and an equivalent intact manual copy.
- [ ] Setup guidance explains one configuration per Git root, immutable source-version recording, approved dry runs, and lazy optional directories.
- [ ] Adoption and update guidance clearly distinguish distribution-managed vendored files from consumer-owned configuration, guidance, backend state, local changes, and artifacts.
- [ ] Update guidance requires reviewed diffs, preserved consumer files, surfaced local modifications, and no automatic migrations.
- [ ] Documentation links the accepted RFC, ARP, specification, dependency table, and consumer verification entry point without duplicating their full content.
- [ ] Link and structural verification passes.

## Blocked by

- [Record immutable distribution identity during project configuration](ISSUE-0001-record-immutable-distribution-identity.md)
- [Publish and verify the v0.1 workflow dependency table](ISSUE-0002-publish-and-verify-workflow-dependencies.md)

## Out of scope

Publishing a release, implementing an installer or updater, or migrating existing consumers.

## Comments

## Resolution
