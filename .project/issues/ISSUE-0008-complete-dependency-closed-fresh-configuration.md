---
id: ISSUE-0008
title: Complete dependency-closed fresh configuration
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent: ../../docs/specifications/v0.2-fresh-project-lifecycle.md
blocked_by:
  - ISSUE-0006-generate-v0.2-manifests-and-release-bundles.md
  - ISSUE-0007-verify-schema-2-consumers-from-installed-assets.md
labels: [v0.2, lifecycle, installation]
---

# Complete dependency-closed fresh configuration

## Parent

[v0.2 fresh-project lifecycle](../../docs/specifications/v0.2-fresh-project-lifecycle.md)

## What to build

Let `configure-workflows` turn an intentionally incomplete fresh installation into a verified dependency-closed schema-2 consumer through an explicit non-destructive dry run.

## Acceptance criteria

- [x] `configure-workflows` obtains user-selected workflow intent and uses the lifecycle command to calculate closure.
- [x] It compares the closure with exact harness-discovered skills and reports missing, unexpected, duplicate, incomplete, and modified directories.
- [x] Missing skills are sourced only from a safely verified current-release archive supplied by local path or HTTPS URL.
- [x] The parent of discovered `configure-workflows` is the default missing-skill destination, with explicit repository-contained per-skill overrides.
- [x] The dry run identifies archive digest, selected workflows, closure, every source and destination, all file actions, and schema-2 configuration and guidance changes.
- [x] Apply rechecks the approved inputs, stages complete skill directories, and creates only absent destinations; occupied, incomplete, or modified destinations block writes.
- [x] Existing skill directories and consumer-owned files are never replaced or removed.
- [x] Failures stop safely and identify any newly created directories with cleanup guidance.
- [x] Configuration completes only after harness discovery confirms the closure and installed verification passes.
- [x] Empty- and existing-project fixtures preserve conventions and keep optional artifact and issue directories lazy.
- [x] Complete structural verification passes.

## Blocked by

- [Generate deterministic v0.2 manifests and release bundles](ISSUE-0006-generate-v0.2-manifests-and-release-bundles.md)
- [Verify schema-2 consumers from installed lifecycle assets](ISSUE-0007-verify-schema-2-consumers-from-installed-assets.md)

## Out of scope

Replacing installed skills, reusable updates, transaction journals, rollback, or automatic schema migration.

## Comments

## Resolution

Resolved on 2026-08-24. The installed lifecycle command now generates immutable `plan-fresh` dry runs and applies exact approved plans through `apply-fresh`. Plans bind release archive bytes, selected intent, calculated and operational closure, discovered and unexpected skills, every destination and file action, and schema-2 configuration/guidance fragments. Apply rechecks all inputs, stages complete skills beside destinations, publishes only absent directories, never writes configuration or replaces existing content, and reports precise cleanup after failure. `configure-workflows` retains approval and discovery confirmation. Ten fresh-install scenarios and all 56 repository tests pass.
