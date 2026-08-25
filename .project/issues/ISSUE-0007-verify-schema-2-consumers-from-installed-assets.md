---
id: ISSUE-0007
title: Verify schema-2 consumers from installed lifecycle assets
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent: ../../docs/specifications/v0.2-fresh-project-lifecycle.md
blocked_by:
  - ISSUE-0006-generate-v0.2-manifests-and-release-bundles.md
labels: [v0.2, lifecycle, verification]
---

# Verify schema-2 consumers from installed lifecycle assets

## Parent

[v0.2 fresh-project lifecycle](../../docs/specifications/v0.2-fresh-project-lifecycle.md)

## What to build

Package a deterministic lifecycle command with `configure-workflows` and make an installed schema-2 consumer able to verify itself without an Agent Workflows source checkout or fixed skill parent directory.

## Acceptance criteria

- [x] The lifecycle command and current manifest are distributed inside `configure-workflows` through relative references.
- [x] The command exposes deterministic human-readable and machine-readable manifest, closure, inspection, and verification operations.
- [x] Schema 2 retains v0.1 distribution, backend, and artifact configuration and adds unique selected workflows plus a skill-to-repository-relative-path inventory.
- [x] Validation rejects unknown selection, incomplete closure, stale or duplicate inventory, path collisions, escaping paths, wrong directory names, mutable identity, and mismatched manifest files.
- [x] Verification checks every distributed file hash, internal relative references, required guidance, backend settings, and lazy disabled capabilities.
- [x] Missing, extra, and modified files are distinguished without mutation.
- [x] Verification accepts exact harness-discovered directories from one or several repository-contained locations without assuming `.agents/skills/`.
- [x] A copied `configure-workflows` and copied closure verify a consumer fixture after the source checkout is made unavailable.
- [x] Existing v0.1 verification remains available until the known migration issue is complete.
- [x] Complete structural verification passes.

## Blocked by

- [Generate deterministic v0.2 manifests and release bundles](ISSUE-0006-generate-v0.2-manifests-and-release-bundles.md)

## Out of scope

Installing missing dependencies, migrating v0.1, or replacing existing skills.

## Comments

## Resolution

Resolved on 2026-08-24. The installed lifecycle command now provides deterministic `show-manifest`, `closure`, `inspect`, and `verify-consumer` operations with human or canonical JSON output. `consumer.py` implements the schema-2 YAML subset, selected-workflow closure, exact discovered-path inventory, manifest-backed file and link integrity, configuration and guidance validation, and non-mutating error categories. Templates and examples use schema 2, and copied lifecycle assets verify without a source checkout. Eleven installed-lifecycle scenarios and all 46 repository tests pass while schema-1 source verification remains available.
