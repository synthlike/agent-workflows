---
id: ARP-0004
title: Ship v0.2 for fresh-project adoption
status: accepted
date: 2026-08-24
supersedes:
  - ARP-0003
superseded_by:
related_rfcs:
  - ../rfcs/RFC-0003-reduce-v0.2-to-fresh-project-lifecycle.md
---

# Ship v0.2 for fresh-project adoption

> Revised by [ARP-0007](ARP-0007-install-the-complete-skill-distribution.md): complete installation replaces the v0.2 archive-backed dependency completion mechanism; the manifest, schema-2 inventory, and installed verification remain accepted.

## Context

The full v0.2 lifecycle design assumed an installed population needing reusable migration and transaction safety. In fact, there is one user and one v0.1.0 installation. The same user may adopt v0.2 in additional fresh Git-backed projects, but productizing a one-time migration and generalized updater would delay fresh-project improvements.

## Decision

v0.2 supports the fresh-project lifecycle:

- `configure-workflows` carries the deterministic lifecycle command and current machine-readable manifest;
- fresh configuration calculates dependency closure, obtains missing skills from the verified current release bundle, presents every destination, and records schema-2 selected workflows and discovered paths;
- installed consumer verification runs without a source checkout; and
- the currently used installer and harness receive a real fresh-project smoke test.

The sole v0.1.0 installation migrates through one reviewed repository-local implementation change, not a public bootstrap interface.

Reusable update planning, replacement, transaction journals, rollback, interruption recovery, self-update, legacy baseline manifests, and standalone bootstrap assets are deferred to v0.3. Until then, v0.2 consumers follow the reviewed manual update contract.

This decision supersedes [ARP-0003](ARP-0003-apply-workflow-updates-transactionally.md) as v0.2 scope. It refines [ARP-0002](ARP-0002-use-configure-workflows-as-the-lifecycle-bootstrap.md): its bootstrap, manifest, schema-2 inventory, and fresh closure decisions remain accepted, while its public v0.1 bootstrap requirement is deferred.

## Rationale

This boundary delivers portable value for every fresh project the actual user may adopt while avoiding a large compatibility and failure-recovery system with no installed audience. The retained manifest, closure, inventory, bundle, and verification seams provide evidence and foundations for designing v0.3 updates against real v0.2 installations.

## Consequences

- v0.2 is suitable for fresh Git-backed consumers but does not promise automated updates.
- The one v0.1.0 migration is implementation work specific to the known installation.
- v0.2 documentation must explicitly retain reviewed manual update guidance.
- v0.3 must revisit update and recovery before the installed population grows materially.
- Integration testing targets the current installer and harness, not a broad compatibility matrix.
