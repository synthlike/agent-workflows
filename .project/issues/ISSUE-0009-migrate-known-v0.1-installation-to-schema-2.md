---
id: ISSUE-0009
title: Migrate the known v0.1.0 installation to schema 2
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent: ../../docs/specifications/v0.2-fresh-project-lifecycle.md
blocked_by:
  - ISSUE-0008-complete-dependency-closed-fresh-configuration.md
labels: [v0.2, migration]
---

# Migrate the known v0.1.0 installation to schema 2

## Parent

[v0.2 fresh-project lifecycle](../../docs/specifications/v0.2-fresh-project-lifecycle.md)

## What to build

Migrate this repository's sole known v0.1.0 consumer configuration through a reviewed local change, proving the v0.2 assets against a real installation without creating a public migration interface.

## Acceptance criteria

- [x] The current installation is verified and its selected-workflow intent and discovered repository-contained skill paths are explicitly recorded.
- [x] The proposed schema-1-to-schema-2 diff is reviewed as ordinary repository work.
- [x] `.agents/workflows.yaml` records schema 2, exact accepted distribution identity, selected workflows, and the complete skill-path inventory.
- [x] Existing guidance, backend state, RFCs, ARPs, specifications, issues, and other consumer-owned files remain intact except for separately reviewed documentation changes.
- [x] Installed verification runs from the packaged `configure-workflows` lifecycle assets and passes without relying on source-only verification paths.
- [x] No legacy baseline manifest, bootstrap release asset, migration command, or generalized updater is introduced.
- [x] The migration and its verification are committed normally.
- [x] Complete structural verification passes.

## Blocked by

- [Complete dependency-closed fresh configuration](ISSUE-0008-complete-dependency-closed-fresh-configuration.md)

## Out of scope

Supporting unknown v0.1 consumers or publishing reusable cross-version migration behavior.

## Comments

## Resolution

Resolved on 2026-08-24 through a reviewed repository-local migration. `.agents/workflows.yaml` now uses schema 2 and v0.2.0 identity, records all 12 non-bootstrap workflows as selected, and maps the complete 13-skill closure under `skills/<skill-name>`. Generated workflow guidance records the same inventory. Default structural verification now invokes the lifecycle command installed in `configure-workflows`; it verifies the exact full closure without the legacy source-comparison path. Schema-1 diagnostics remain available, and no public migration or updater assets were introduced. All 56 tests pass.
