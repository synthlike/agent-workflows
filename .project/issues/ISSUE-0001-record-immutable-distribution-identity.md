---
id: ISSUE-0001
title: Record immutable distribution identity during project configuration
kind: task
status: open
created: 2026-08-24
assignee:
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

- [ ] The canonical workflow configuration template requires `distribution.source` and `distribution.version`.
- [ ] Bundled examples represent a valid immutable distribution identity or are explicitly marked as incomplete examples that setup must replace.
- [ ] Consumer configuration verification accepts exact release identifiers and immutable commit SHAs.
- [ ] Consumer configuration verification rejects mutable identities such as `latest`, branch names, and `unreleased` for completed installations.
- [ ] Existing consumer-owned configuration is changed only through an approved `configure-project` dry run.
- [ ] Relevant structural verification and fixture tests pass.

## Blocked by

None.

## Out of scope

Creating the first release tag, implementing updates, or defining a package registry.

## Comments

## Resolution
