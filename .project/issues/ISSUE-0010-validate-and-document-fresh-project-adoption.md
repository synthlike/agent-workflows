---
id: ISSUE-0010
title: Validate and document fresh-project adoption
kind: task
status: open
created: 2026-08-24
assignee:
parent: ../../docs/specifications/v0.2-fresh-project-lifecycle.md
blocked_by:
  - ISSUE-0008-complete-dependency-closed-fresh-configuration.md
  - ISSUE-0009-migrate-known-v0.1-installation-to-schema-2.md
labels: [v0.2, installation, documentation]
---

# Validate and document fresh-project adoption

## Parent

[v0.2 fresh-project lifecycle](../../docs/specifications/v0.2-fresh-project-lifecycle.md)

## What to build

Prove and document the complete v0.2 fresh-project path through the installer and harness actually used by the decision owner, while making the deferred update boundary explicit.

## Acceptance criteria

- [ ] A real Agent Skills-compatible installer smoke test starts with `configure-project` and an intentionally incomplete selected set in a temporary Git repository.
- [ ] The installed lifecycle calculates closure, adds only missing skills, records schema 2, receives harness discovery confirmation, and verifies without a source checkout.
- [ ] Smoke scenarios cover the default sibling destination, path override, multiple discovered locations, occupied destination, changed dry-run input, and staged-copy failure.
- [ ] Existing-project adoption preserves surrounding guidance, artifact conventions, backend state, and project files.
- [ ] README and setup documentation explain the manifest, automatic closure, schema-2 inventory, dry run, discovery confirmation, installed verification, and lazy directories.
- [ ] Update documentation clearly retains reviewed manual updates and states that reusable planning, replacement, rollback, recovery, and migration are deferred to v0.3.
- [ ] Current RFC, ARP, specification, issue, manifest, and verification links are valid without duplicating authoritative content.
- [ ] Changelog and release verification cover the completed v0.2 fresh-project contract.
- [ ] All structural, unit, fixture, integration, and documentation-link checks pass from a clean tree.

## Blocked by

- [Complete dependency-closed fresh configuration](ISSUE-0008-complete-dependency-closed-fresh-configuration.md)
- [Migrate the known v0.1.0 installation to schema 2](ISSUE-0009-migrate-known-v0.1-installation-to-schema-2.md)

## Out of scope

A broad harness matrix, reusable updater, transaction engine, public v0.1 migration, or v0.2 release publication.

## Comments

## Resolution
