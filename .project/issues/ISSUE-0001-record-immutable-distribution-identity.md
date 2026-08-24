---
id: ISSUE-0001
title: Record immutable distribution identity during project configuration
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent: ../../docs/specifications/v0.1-installation-and-consumer-project-contract.md
blocked_by: []
labels: [v0.1, installation]
---

# Record immutable distribution identity during project configuration

## Parent

[v0.1 installation and consumer-project contract](../../docs/specifications/v0.1-installation-and-consumer-project-contract.md)

## What to build

Make distribution identity a consistent, verifiable result of configuring a consumer project. Configuration templates, bundled examples, and setup guidance must record the distribution source and either an exact release identifier or immutable commit SHA.

## Acceptance criteria

- [x] The canonical workflow configuration template requires `distribution.source` and `distribution.version`.
- [x] Bundled examples represent a valid immutable distribution identity or are explicitly marked as incomplete examples that setup must replace.
- [x] Consumer configuration verification accepts exact release identifiers and immutable commit SHAs.
- [x] Consumer configuration verification rejects mutable identities such as `latest`, branch names, and `unreleased` for completed installations.
- [x] Existing consumer-owned configuration is changed only through an approved `configure-project` dry run.
- [x] Relevant structural verification and fixture tests pass.

## Blocked by

None.

## Out of scope

Creating the first release tag, implementing updates, or defining a package registry.

## Comments

## Resolution

Resolved on 2026-08-24. `configure-project` now requires immutable distribution identity in exploration, dry runs, and writes. Templates and examples expose required placeholders and identify themselves as incomplete. `scripts/verify_workflow_config.py` accepts exact semantic release versions or 40/64-character commit SHAs and rejects mutable or placeholder values; source verification and five identity tests pass.
