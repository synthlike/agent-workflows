---
id: ARP-0003
title: Apply workflow updates transactionally
status: accepted
date: 2026-08-24
supersedes: []
superseded_by: ARP-0004
related_rfcs:
  - ../rfcs/RFC-0002-v0.2-lifecycle-management-contract.md
---

# Apply workflow updates transactionally

> Superseded for v0.2 by [ARP-0004](ARP-0004-ship-v0.2-for-fresh-project-adoption.md). Reusable transactional updates are deferred to v0.3.

## Context

A workflow update may replace several skill directories at different harness-discovered paths. Delegating replacement to a third-party installer cannot guarantee the v0.1 ownership boundary, and a partial or interrupted update could leave an unusable dependency set. Local modifications and consumer-owned files must never be silently lost.

## Decision

The v0.2 lifecycle command owns update replacement through a two-phase transaction:

1. accept a self-contained target bundle by local path or HTTPS URL;
2. stage it, verify its manifest, and bind an immutable update plan to the complete bundle's SHA-256;
3. present the plan through `configure-project` for explicit approval;
4. before apply, recheck the target bundle and current installed-file hashes;
5. journal the operation, stage replacements beside each destination, and retain backups;
6. replace only approved distribution-managed skill directories;
7. update consumer configuration last; and
8. remove backups only after successful verification.

A caught failure restores the previous installation. A later lifecycle invocation recovers an interrupted transaction before performing other work. Consumer-owned artifacts are never part of the transaction. Locally modified skills block replacement unless the consumer separately and explicitly approves discarding them; v0.2 does not merge conflicts.

## Rationale

A deterministic transaction is the only option considered that provides installer-independent replacement, protects the dependency closure from partial updates, and makes recovery testable. A skill-only mutation varies by harness, while external-installer delegation cannot enforce ownership or recovery semantics.

## Consequences

- Apply requires a transaction journal, per-destination staging, and backups.
- Plans become invalid when current files or the staged bundle change.
- Configuration identity cannot advance before skill replacement succeeds.
- Recovery behavior must be tested across failures at every transaction phase.
- Update code may replace its own installed directory and therefore must execute safely from staged or already-loaded code.
- Automatic conflict merging and artifact migration remain out of scope.
