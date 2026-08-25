---
id: RFC-0003
title: Reduce v0.2 to the fresh-project lifecycle
status: accepted
authors: [synthlike]
created: 2026-08-24
decision_owner: synthlike
related_arps:
  - ../decisions/ARP-0004-ship-v0.2-for-fresh-project-adoption.md
---

# Reduce v0.2 to the fresh-project lifecycle

## Summary

Amend the accepted [v0.2 lifecycle-management RFC](RFC-0002-v0.2-lifecycle-management-contract.md) after learning that there is one v0.1.0 user and one existing installation to migrate.

v0.2 should make Agent Workflows self-contained and safe for fresh Git-backed consumer projects. It should not build a reusable cross-version updater, transaction engine, or public v0.1.0 bootstrap before multiple installed consumers exist. The sole v0.1.0 installation can migrate through one reviewed implementation change. General reusable updates become a v0.3 concern.

## Motivation

RFC-0002 assumed that v0.2 needed to support an installed population with diverse harness locations and unknown local modifications. That assumption drove substantial requirements:

- a standalone v0.1.0 bootstrap release asset;
- a legacy baseline manifest;
- immutable cross-version update plans;
- multi-directory transaction journals and backups;
- automatic rollback and interruption recovery;
- self-replacement of the executing lifecycle command; and
- broad update and failure-injection integration matrices.

The decision owner is the only v0.1.0 user. Building that generalized update system now would solve a hypothetical compatibility problem and delay the parts that make Agent Workflows useful in fresh projects: machine-readable releases, automatic closure, installed verification, and coherent initial configuration.

## Requirements and constraints

### Requirements

- v0.2 MUST support fresh adoption in Git-backed repositories beyond this source repository.
- `configure-workflows` MUST remain mandatory and carry the deterministic lifecycle command plus current release manifest.
- Each release MUST publish machine-readable identity, configuration compatibility, direct dependencies, and distributed-file SHA-256 data.
- Fresh configuration MUST calculate closure from user-selected workflows rather than requiring manual dependency calculation.
- Missing dependencies MUST come from a verified current-release bundle.
- The dry run MUST show every skill destination and configuration change before writing.
- The already discovered `configure-workflows` parent MUST be the default destination for missing skills, with explicit repository-contained overrides.
- Configuration MUST complete only after the consumer's harness confirms discovery of the closure.
- v0.2 MUST use schema 2 with selected workflows and discovered skill paths in the single root `.agents/workflows.yaml`.
- Consumer verification MUST run from installed lifecycle assets without a source checkout.
- Initial installation and configuration MUST preserve pre-existing guidance, conventions, backend state, and artifacts.
- The fresh-project flow MUST be smoke-tested through the currently used Agent Skills-compatible installer and harness.
- The sole v0.1.0 installation MUST migrate through a reviewed, repository-local implementation change before or with v0.2 adoption.
- Documentation MUST state that reusable automated updates are deferred to v0.3 and retain the reviewed manual update contract in the meantime.

### Constraints

- There is one known user and one known v0.1.0 installation.
- The same user may adopt v0.2 in multiple fresh consumer repositories once the fresh flow is ready.
- Future consumer repositories may choose different repository-contained skill paths, so one source-repository-specific path must not become contractual.
- Third-party installer behavior remains illustrative rather than guaranteed.
- The v0.1 vendored and consumer-owned boundary remains accepted.
- v0.2 implementation should create seams reusable by a v0.3 updater without implementing that updater prematurely.

### Assumptions

- No unknown external v0.1.0 consumers require an automated migration path.
- The decision owner can review and commit the one v0.1.0 migration directly.
- Git provides adequate review and recovery for initial v0.2 configuration.
- New v0.2 consumers can continue using reviewed manual updates until v0.3.

### Preferences

- Prefer fresh-project value over speculative compatibility machinery.
- Prefer reusable manifest, closure, and verification primitives that v0.3 can compose.
- Prefer explicit documentation of deferred update guarantees over a partial updater.
- Prefer one real harness integration path over a broad matrix without users.

## Non-goals

- A standalone v0.1.0 bootstrap release asset.
- A generated legacy v0.1.0 baseline manifest as a public compatibility interface.
- Automated v0.1-to-v0.2 migration.
- Reusable update planning or file replacement in v0.2.
- Transaction journals, backups, rollback, interruption recovery, or self-update behavior in v0.2.
- A cross-harness installer integration matrix.
- Automatic conflict merging or artifact migration.
- Multiple or nested workflow configurations in one Git repository.

## Open questions

None.

## Options

### Option A: Fresh-project lifecycle in v0.2; reusable updates in v0.3

Implement manifests, release bundles, closure calculation, schema-2 inventory, installed verification, and dependency-complete fresh configuration. Migrate the sole v0.1.0 installation through a reviewed local change. Continue documented manual updates until v0.3.

Advantages:

- delivers immediate value for every new project the decision owner adopts;
- substantially reduces v0.2 complexity and risk;
- avoids productizing a migration used once;
- keeps useful primitives for a later updater; and
- preserves the v0.1 ownership boundary.

Disadvantages:

- v0.2 consumers still lack automated updates;
- RFC-0002 and its transactional-update decision must be narrowed or superseded;
- the one existing installation needs explicit manual work; and
- v0.3 must revisit update planning and recovery before a larger installed base develops.

### Option B: Implement the complete accepted RFC-0002 lifecycle

Build fresh installation, reusable v0.1 bootstrap, immutable update planning, transactional replacement, rollback, and recovery in v0.2.

Advantages:

- completes the entire lifecycle in one release;
- establishes strong update guarantees before more consumers exist; and
- avoids deferring difficult transaction work.

Disadvantages:

- optimizes for users and migrations that do not exist;
- delays fresh-project improvements;
- carries a large failure surface; and
- requires maintaining public bootstrap behavior used only once.

### Option C: Optimize v0.2 only for this repository

Implement repository-specific scripts and paths without a general fresh-project contract.

Advantages:

- minimizes immediate implementation effort;
- can use known paths and Git state; and
- avoids release packaging work.

Disadvantages:

- v0.2 cannot be adopted in other fresh projects;
- undermines the toolkit's portability goal;
- creates throwaway behavior that v0.3 must replace; and
- provides little release value beyond internal maintenance.

### Option D: Make no lifecycle changes in v0.2

Keep the v0.1 manual model and spend v0.2 on unrelated workflows.

Advantages:

- requires no lifecycle implementation; and
- avoids revisiting accepted decisions.

Disadvantages:

- leaves dependency calculation and verification awkward for every new project;
- abandons the confirmed lifecycle theme; and
- postpones all enabling primitives alongside the updater.

## Recommendation

Choose Option A.

The revised boundary matches actual demand: support any fresh Git-backed project the sole user chooses to adopt, while treating the only legacy migration as implementation work rather than a public product surface. Manifest, closure, inventory, bundle, and installed-verification seams remain durable investments and make a v0.3 updater easier to design from real v0.2 installations.

## Resolution

Accepted by the decision owner on 2026-08-24. v0.2 adopts Option A: support dependency-complete, self-verifying fresh Git-backed projects; migrate the sole v0.1.0 installation through reviewed local work; and defer reusable update planning, replacement, rollback, recovery, and public legacy bootstrap behavior to v0.3.

The scope decision is recorded in [ARP-0004](../decisions/ARP-0004-ship-v0.2-for-fresh-project-adoption.md). Current behavior is defined by the [v0.2 fresh-project lifecycle](../specifications/v0.2-fresh-project-lifecycle.md).

Implementation work:

- [Generate deterministic v0.2 manifests and release bundles](../../.project/issues/ISSUE-0006-generate-v0.2-manifests-and-release-bundles.md)
- [Verify schema-2 consumers from installed lifecycle assets](../../.project/issues/ISSUE-0007-verify-schema-2-consumers-from-installed-assets.md)
- [Complete dependency-closed fresh configuration](../../.project/issues/ISSUE-0008-complete-dependency-closed-fresh-configuration.md)
- [Migrate the known v0.1.0 installation to schema 2](../../.project/issues/ISSUE-0009-migrate-known-v0.1-installation-to-schema-2.md)
- [Validate and document fresh-project adoption](../../.project/issues/ISSUE-0010-validate-and-document-fresh-project-adoption.md)
