---
id: ISSUE-0008
title: Complete dependency-closed fresh configuration
kind: task
status: open
created: 2026-08-24
assignee:
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

Let `configure-project` turn an intentionally incomplete fresh installation into a verified dependency-closed schema-2 consumer through an explicit non-destructive dry run.

## Acceptance criteria

- [ ] `configure-project` obtains user-selected workflow intent and uses the lifecycle command to calculate closure.
- [ ] It compares the closure with exact harness-discovered skills and reports missing, unexpected, duplicate, incomplete, and modified directories.
- [ ] Missing skills are sourced only from a safely verified current-release archive supplied by local path or HTTPS URL.
- [ ] The parent of discovered `configure-project` is the default missing-skill destination, with explicit repository-contained per-skill overrides.
- [ ] The dry run identifies archive digest, selected workflows, closure, every source and destination, all file actions, and schema-2 configuration and guidance changes.
- [ ] Apply rechecks the approved inputs, stages complete skill directories, and creates only absent destinations; occupied, incomplete, or modified destinations block writes.
- [ ] Existing skill directories and consumer-owned files are never replaced or removed.
- [ ] Failures stop safely and identify any newly created directories with cleanup guidance.
- [ ] Configuration completes only after harness discovery confirms the closure and installed verification passes.
- [ ] Empty- and existing-project fixtures preserve conventions and keep optional artifact and issue directories lazy.
- [ ] Complete structural verification passes.

## Blocked by

- [Generate deterministic v0.2 manifests and release bundles](ISSUE-0006-generate-v0.2-manifests-and-release-bundles.md)
- [Verify schema-2 consumers from installed lifecycle assets](ISSUE-0007-verify-schema-2-consumers-from-installed-assets.md)

## Out of scope

Replacing installed skills, reusable updates, transaction journals, rollback, or automatic schema migration.

## Comments

## Resolution
