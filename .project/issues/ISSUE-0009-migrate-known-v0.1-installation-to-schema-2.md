---
id: ISSUE-0009
title: Migrate the known v0.1.0 installation to schema 2
kind: task
status: open
created: 2026-08-24
assignee:
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

- [ ] The current installation is verified and its selected-workflow intent and discovered repository-contained skill paths are explicitly recorded.
- [ ] The proposed schema-1-to-schema-2 diff is reviewed as ordinary repository work.
- [ ] `.agents/workflows.yaml` records schema 2, exact accepted distribution identity, selected workflows, and the complete skill-path inventory.
- [ ] Existing guidance, backend state, RFCs, ARPs, specifications, issues, and other consumer-owned files remain intact except for separately reviewed documentation changes.
- [ ] Installed verification runs from the packaged `configure-project` lifecycle assets and passes without relying on source-only verification paths.
- [ ] No legacy baseline manifest, bootstrap release asset, migration command, or generalized updater is introduced.
- [ ] The migration and its verification are committed normally.
- [ ] Complete structural verification passes.

## Blocked by

- [Complete dependency-closed fresh configuration](ISSUE-0008-complete-dependency-closed-fresh-configuration.md)

## Out of scope

Supporting unknown v0.1 consumers or publishing reusable cross-version migration behavior.

## Comments

## Resolution
