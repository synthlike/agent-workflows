---
id: ISSUE-0003
title: Add consumer-installation structural verification
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent: ../../docs/specifications/v0.1-installation-and-consumer-project-contract.md
blocked_by:
  - ISSUE-0001-record-immutable-distribution-identity.md
  - ISSUE-0002-publish-and-verify-workflow-dependencies.md
labels: [v0.1, installation, verification]
---

# Add consumer-installation structural verification

## Parent

[v0.1 installation and consumer-project contract](../../docs/specifications/v0.1-installation-and-consumer-project-contract.md)

## What to build

Provide consumer-oriented structural verification that validates an installed workflow selection and configured repository without assuming this source repository's layout or one physical skill parent directory.

## Acceptance criteria

- [x] Verification accepts a consumer root and a harness-discoverable installed skill set without requiring `.agents/skills/`.
- [x] Verification checks dependency closure, intact skill directories, matching skill names, and resolvable internal references.
- [x] Verification checks one root configuration, repository-contained relative paths, backend guidance, enabled artifact settings, and immutable distribution identity.
- [x] A fresh-project fixture verifies approved setup writes only declared files and creates no optional artifact directories.
- [x] An existing-project fixture verifies surrounding guidance and existing artifact conventions are preserved without migration.
- [x] Scenarios cover disabled capabilities, nested configuration rejection, mutable-version rejection, and surfaced conflicts with locally modified vendored skills.
- [x] The existing source-distribution verification continues to pass.

## Blocked by

- [Record immutable distribution identity during project configuration](ISSUE-0001-record-immutable-distribution-identity.md)
- [Publish and verify the v0.1 workflow dependency table](ISSUE-0002-publish-and-verify-workflow-dependencies.md)

## Out of scope

Implementing a universal agent-discovery API, updater, rollback system, or automatic conflict merger.

## Comments

## Resolution

Resolved on 2026-08-24. `scripts/verify_consumer_installation.py` validates an explicit harness-discovered skill set at arbitrary locations against the release dependency table and source skills, checks root configuration and guidance, and surfaces local skill changes. `docs/verifying-installation.md` documents both shared-parent and repeated-directory invocation. Nine consumer scenarios cover fresh and existing projects, dependency and skill integrity, disabled capabilities, nested configuration, escaping paths, mutable versions, and update conflicts. The complete suite passes with 20 tests.
