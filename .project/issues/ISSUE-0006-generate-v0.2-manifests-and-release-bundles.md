---
id: ISSUE-0006
title: Generate deterministic v0.2 manifests and release bundles
kind: task
status: open
created: 2026-08-24
assignee:
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

- [ ] A documented manifest schema identifies format version, distribution source/version, supported configuration schemas, every skill, and direct dependencies.
- [ ] Every distributed file inside each skill directory except the manifest itself is listed by skill-relative path with SHA-256.
- [ ] Installer locks and external symlinks, caches, OS metadata, consumer files, backend state, and artifacts are excluded.
- [ ] Manifest generation is deterministic and fails for unknown or missing skills, stale dependency declarations, duplicate or escaping paths, and unlisted distributed files.
- [ ] A deterministic release archive contains the manifest, complete skill directories, lifecycle assets through `configure-project`, and changelog information.
- [ ] Bundle validation accepts local archives and safely staged HTTPS bytes while rejecting traversal, links, devices, duplicate members, unexpected content, and digest mismatches.
- [ ] Existing Markdown dependency documentation is generated from or verified against the same authoritative dependency data rather than becoming a second divergent source.
- [ ] Unit and fixture tests cover deterministic generation and all rejection cases.
- [ ] Complete structural verification passes.

## Blocked by

None.

## Out of scope

Fresh-project mutation, schema-2 consumer verification, cryptographic signing, or cross-version updates.

## Comments

## Resolution
