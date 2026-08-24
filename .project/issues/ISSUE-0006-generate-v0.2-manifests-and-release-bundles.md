---
id: ISSUE-0006
title: Generate deterministic v0.2 manifests and release bundles
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent: ../../docs/specifications/v0.2-fresh-project-lifecycle.md
blocked_by: []
labels: [v0.2, lifecycle, packaging]
---

# Generate deterministic v0.2 manifests and release bundles

## Parent

[v0.2 fresh-project lifecycle](../../docs/specifications/v0.2-fresh-project-lifecycle.md)

## What to build

Produce one machine-readable description and one self-contained archive for a v0.2 release so fresh consumers can calculate closure and verify exact distributed skill contents without a source checkout.

## Acceptance criteria

- [x] A documented manifest schema identifies format version, distribution source/version, supported configuration schemas, every skill, and direct dependencies.
- [x] Every distributed file inside each skill directory except the manifest itself is listed by skill-relative path with SHA-256.
- [x] Installer locks and external symlinks, caches, OS metadata, consumer files, backend state, and artifacts are excluded.
- [x] Manifest generation is deterministic and fails for unknown or missing skills, stale dependency declarations, duplicate or escaping paths, and unlisted distributed files.
- [x] A deterministic release archive contains the manifest, complete skill directories, lifecycle assets through `configure-project`, and changelog information.
- [x] Bundle validation accepts local archives and safely staged HTTPS bytes while rejecting traversal, links, devices, duplicate members, unexpected content, and digest mismatches.
- [x] Existing Markdown dependency documentation is generated from or verified against the same authoritative dependency data rather than becoming a second divergent source.
- [x] Unit and fixture tests cover deterministic generation and all rejection cases.
- [x] Complete structural verification passes.

## Blocked by

None.

## Out of scope

Fresh-project mutation, schema-2 consumer verification, cryptographic signing, or cross-version updates.

## Comments

## Resolution

Resolved on 2026-08-24. `release/metadata.json` defines v0.2.0 release identity, schema compatibility, and the exact skill inventory. The lifecycle command bundled under `configure-project` deterministically generates and checks the canonical manifest, builds normalized `tar.gz` release bundles, validates local or HTTPS bundle bytes, rejects unsafe archive content, verifies manifest/file/dependency integrity, and stages files without general tar extraction. `docs/release-manifest.md` documents schema and operations. Fifteen release-specific tests and all 35 repository tests pass.
