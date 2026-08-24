---
id: ISSUE-0002
title: Publish and verify the v0.1 workflow dependency table
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
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

- [x] Release documentation publishes every v0.1 skill and its additional direct skill dependencies.
- [x] Documentation states that `configure-project` is required for every installation and that cycles are valid.
- [x] A verification check fails when a dependency names an unknown skill, an installed skill lacks a table row, or an explicit cross-skill invocation is missing from the table.
- [x] Verification can calculate and report the transitive closure for any selected skill set.
- [x] Documentation-only artifact references do not create false workflow dependencies.
- [x] Relevant structural verification passes.

## Blocked by

None.

## Out of scope

A custom package manifest or automatic dependency resolver for third-party installers.

## Comments

## Resolution

Resolved on 2026-08-24. `docs/workflow-dependencies.md` now publishes the v0.1 direct dependency table and defines the inline-code routing convention. `scripts/verify_workflow_dependencies.py` validates table completeness and synchronization, rejects unknown dependencies, and reports transitive closures with implicit `configure-project` inclusion and cycle support. Six dependency tests and the complete structural verification suite pass.
