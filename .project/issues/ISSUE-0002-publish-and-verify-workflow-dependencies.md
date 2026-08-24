---
id: ISSUE-0002
title: Publish and verify the v0.1 workflow dependency table
kind: task
status: open
created: 2026-08-24
assignee:
parent: ../../docs/specifications/v0.1-installation-and-consumer-project-contract.md
blocked_by: []
labels: [v0.1, installation]
---

# Publish and verify the v0.1 workflow dependency table

## Parent

[v0.1 installation and consumer-project contract](../../docs/specifications/v0.1-installation-and-consumer-project-contract.md)

## What to build

Give installers and manual operators one release-facing table from which they can select an intact, dependency-closed workflow set. Keep that table synchronized with explicit cross-skill routing in the distributed skills.

## Acceptance criteria

- [ ] Release documentation publishes every v0.1 skill and its additional direct skill dependencies.
- [ ] Documentation states that `configure-project` is required for every installation and that cycles are valid.
- [ ] A verification check fails when a dependency names an unknown skill, an installed skill lacks a table row, or an explicit cross-skill invocation is missing from the table.
- [ ] Verification can calculate and report the transitive closure for any selected skill set.
- [ ] Documentation-only artifact references do not create false workflow dependencies.
- [ ] Relevant structural verification passes.

## Blocked by

None.

## Out of scope

A custom package manifest or automatic dependency resolver for third-party installers.

## Comments

## Resolution
