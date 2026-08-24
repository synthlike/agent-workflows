---
id: ARP-0002
title: Use configure-project as the lifecycle bootstrap
status: accepted
date: 2026-08-24
supersedes: []
superseded_by:
related_rfcs:
  - ../rfcs/RFC-0002-v0.2-lifecycle-management-contract.md
---

# Use configure-project as the lifecycle bootstrap

> Refined by [ARP-0004](ARP-0004-ship-v0.2-for-fresh-project-adoption.md): v0.2 retains the fresh bootstrap, manifest, and schema-2 inventory, while reusable legacy bootstrap behavior is deferred to v0.3.

## Context

v0.1 requires every installation to include `configure-project`, but dependency calculation, consumer verification, and updates still depend on Markdown instructions or a separate source checkout. A new lifecycle skill would itself need to be installed before it could resolve an incomplete installation, while a standalone CLI would weaken the skill-first model.

## Decision

In v0.2, `configure-project` remains mandatory and becomes the human-facing lifecycle entrypoint. Its intact skill directory carries:

- a deterministic lifecycle command;
- the current machine-readable release manifest; and
- the workflow guidance for installation, configuration, verification, update planning, approval, and recovery.

The manifest records release identity, configuration-schema compatibility, direct skill dependencies, and SHA-256 hashes for every distributed file inside each skill directory except the manifest itself. v0.2 uses configuration schema 2 with a reviewed inventory of user-selected workflows and discovered skill paths; it does not add a separate toolkit lock file.

The command is also published as a standalone v0.2 release asset, with a generated v0.1.0 baseline manifest, to bootstrap consumers whose installed `configure-project` does not yet carry lifecycle tooling.

During fresh configuration, the command calculates closure and obtains missing dependencies from the current release bundle. It proposes destinations beside the discovered `configure-project` directory by default, permits explicit per-skill overrides, and does not complete configuration until the consumer's harness confirms discovery of the installed closure.

## Rationale

The hybrid keeps human decisions and approval in a semantic skill while moving integrity-sensitive operations behind a deterministic, testable seam. Carrying the command and manifest in the already mandatory skill avoids needing dependency resolution to install the dependency resolver. Schema-2 inventory preserves harness-independent locations and user selection without introducing an ambiguously owned second state file.

## Consequences

- `configure-project` gains lifecycle responsibilities beyond initial setup.
- Every release must generate and verify a manifest and self-contained release bundle.
- Selective installations remain valid only when `configure-project` is intact.
- Fresh-install dry runs must expose every proposed skill destination and verify post-install discovery.
- The v0.1.0 bootstrap must propose schema migration separately and write only after approval.
- Installer locks, caches, external symlinks, configuration, guidance, backend state, and artifacts remain outside manifest integrity.
- Cryptographic release signing is not provided in v0.2.
