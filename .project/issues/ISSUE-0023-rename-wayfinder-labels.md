---
id: ISSUE-0023
title: Rename legacy Wayfinder labels
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent: ../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md
blocked_by: []
labels: [v0.3, consistency]
---

# Rename legacy Wayfinder labels

## Parent

[v0.3 project-foundation and feedback workflows](../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md)

## What to build

Align GitHub issue labels with the adapted `plan-initiative` vocabulary while retaining accurate upstream attribution for Matt Pocock's Wayfinder concept.

## Acceptance criteria

- [x] GitHub map and decision-ticket labels use the `initiative:` namespace.
- [x] The source backend and bundled `configure-project` adapter remain byte-for-byte aligned.
- [x] Wayfinder remains named only where needed for historical attribution or explicit migration guidance.
- [x] The distribution manifest is regenerated and all verification passes.

## Blocked by

None.

## Out of scope

- Renaming `plan-initiative` or changing its behavior.
- Migrating labels in consumer repositories automatically.

## Comments

## Resolution

Resolved on 2026-08-24. GitHub initiative maps and decision tickets now use `initiative:map`, `initiative:research`, `initiative:prototype`, `initiative:clarification`, and `initiative:task`. Source and bundled backend guidance remain identical, structural verification rejects the legacy label namespace, and Wayfinder remains named only in upstream attribution. The v0.3 manifest was regenerated and all 75 tests pass.
