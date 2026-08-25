---
id: ARP-0001
title: Use a vendored consumer-owned installation boundary
status: accepted
date: 2026-08-24
supersedes: []
superseded_by:
related_rfcs:
  - ../rfcs/RFC-0001-v0.1-installation-and-consumer-project-contract.md
---

# Use a vendored consumer-owned installation boundary

## Context

v0.1 needs a stable boundary between this distribution, installation mechanisms, and consumer repositories. The boundary must support selective installation without coupling the kit to one agent harness, physical skill path, or third-party installer. It must also prevent installation and updates from silently changing project-owned configuration or artifacts.

## Decision

v0.1 uses a behavior-based vendored installation contract:

- each installation includes `configure-workflows` and an intact, dependency-closed set of selected skill directories;
- the agent harness or installer chooses the discoverable physical skill location;
- each Git repository has one root `.agents/workflows.yaml`, established through an approved `configure-workflows` dry run before other workflows are used;
- vendored skill directories are distribution-managed, while configuration, generated guidance, backend state, local modifications, and project artifacts are consumer-owned; and
- updates are reviewed replacements, preserve consumer-owned files, surface local modifications, and perform no automatic migration.

The configuration records the immutable distribution source and exact release version or commit SHA.

## Rationale

This boundary preserves harness independence and allows both selective and manual installation while making dependency completeness, reproducibility, and ownership explicit. A fixed-path full installation would be simpler to validate but would couple the kit to one filesystem convention and install unwanted workflows. An installer-specific contract would delegate the user experience but make this project depend on an external interface it does not control. Leaving the boundary informal would keep the existing safety and compatibility ambiguities.

## Consequences

- The release must publish and maintain a dependency table until a supported installer can resolve dependencies automatically.
- Installation documentation may show third-party commands only as examples.
- Consumer-oriented verification must validate the behavioral contract without assuming this source repository's layout.
- v0.1 does not provide nested configurations, automatic updates, conflict merging, schema migration, or artifact migration.
- Changes to the ownership boundary or configuration-root model require reconsidering this decision.
