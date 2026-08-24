---
id: ISSUE-0012
title: Prepare the v0.2.0 release
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent: ../../docs/specifications/v0.2-fresh-project-lifecycle.md
blocked_by: []
labels: [v0.2, release]
---

# Prepare the v0.2.0 release

## Parent

[v0.2 fresh-project lifecycle](../../docs/specifications/v0.2-fresh-project-lifecycle.md)

## What to build

Turn the accepted and implemented v0.2 fresh-project lifecycle into a reproducible `v0.2.0` release with aligned changelog, deterministic release asset, verification evidence, release commit, and local annotated tag.

## Acceptance criteria

- [x] All v0.2 implementation issues are resolved and current RFC, ARP, specification, metadata, manifest, and documentation agree on the release boundary.
- [x] `CHANGELOG.md` contains a dated `0.2.0` release entry.
- [x] The deterministic `agent-workflows-v0.2.0.tar.gz` asset is built and validates against its embedded manifest.
- [x] All structural, unit, installed, release, syntax, and documentation-link verification passes from a clean tree.
- [x] A release commit is created and annotated tag `v0.2.0` points to it.

## Blocked by

None.

## Out of scope

- General update, rollback, recovery, self-update, or public migration tooling deferred to v0.3.
- Publishing through a hosting-service API from this repository checkout.

## Comments

## Resolution

Resolved on 2026-08-24. All v0.2 implementation issues are resolved and the accepted fresh-project boundary agrees with release metadata `v0.2.0`. The changelog has a dated `0.2.0` entry. The deterministic asset `/tmp/agent-workflows-v0.2.0.tar.gz` validates with SHA-256 `1a37f180b7d8d83a898df5b644e795c7c3baca4c18ff7a0defbd6340960ded78`. All 56 tests and structural, installed, release, syntax, and documentation-link checks pass. The verified release commit is tagged `v0.2.0`; pushing and hosted-release publication remain explicit external operations.
