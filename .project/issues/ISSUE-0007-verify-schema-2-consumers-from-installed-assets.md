---
id: ISSUE-0007
title: Verify schema-2 consumers from installed lifecycle assets
kind: task
status: open
created: 2026-08-24
assignee:
parent: ../../docs/specifications/v0.2-fresh-project-lifecycle.md
blocked_by:
  - ISSUE-0006-generate-v0.2-manifests-and-release-bundles.md
labels: [v0.2, lifecycle, verification]
---

# Verify schema-2 consumers from installed lifecycle assets

## Parent

[v0.2 fresh-project lifecycle](../../docs/specifications/v0.2-fresh-project-lifecycle.md)

## What to build

Package a deterministic lifecycle command with `configure-project` and make an installed schema-2 consumer able to verify itself without an Agent Workflows source checkout or fixed skill parent directory.

## Acceptance criteria

- [ ] The lifecycle command and current manifest are distributed inside `configure-project` through relative references.
- [ ] The command exposes deterministic human-readable and machine-readable manifest, closure, inspection, and verification operations.
- [ ] Schema 2 retains v0.1 distribution, backend, and artifact configuration and adds unique selected workflows plus a skill-to-repository-relative-path inventory.
- [ ] Validation rejects unknown selection, incomplete closure, stale or duplicate inventory, path collisions, escaping paths, wrong directory names, mutable identity, and mismatched manifest files.
- [ ] Verification checks every distributed file hash, internal relative references, required guidance, backend settings, and lazy disabled capabilities.
- [ ] Missing, extra, and modified files are distinguished without mutation.
- [ ] Verification accepts exact harness-discovered directories from one or several repository-contained locations without assuming `.agents/skills/`.
- [ ] A copied `configure-project` and copied closure verify a consumer fixture after the source checkout is made unavailable.
- [ ] Existing v0.1 verification remains available until the known migration issue is complete.
- [ ] Complete structural verification passes.

## Blocked by

- [Generate deterministic v0.2 manifests and release bundles](ISSUE-0006-generate-v0.2-manifests-and-release-bundles.md)

## Out of scope

Installing missing dependencies, migrating v0.1, or replacing existing skills.

## Comments

## Resolution
