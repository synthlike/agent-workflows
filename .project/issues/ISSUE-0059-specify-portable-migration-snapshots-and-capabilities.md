---
id: ISSUE-0059
title: "Specify portable migration snapshots and capabilities"
kind: "implementation"
status: resolved
created: 2026-08-25
assignee: "pi"
parent: "ISSUE-0058-implement-strict-cross-backend-record-migration.md"
blocked_by:
labels: ["migration","contract"]
---
# Specify portable migration snapshots and capabilities

## Parent

Implement strict cross-backend record migration

## What to build

Define the versioned, provider-neutral migration snapshot, adapter-owned export/import/retirement capabilities, semantic-fidelity rules, journal schema, stage invariants, and conformance matrix established by ARP-0010.

## Acceptance criteria

- [ ] The specification covers one strict semantic route, active and retained history, exact content, canonical provenance, structured relationships, source/destination references, revisions, states, comments, labels, assignees, timestamps, and provider metadata classification.
- [ ] Adapter-owned capability declarations distinguish issue and non-issue migration export, import, verification, and retirement support.
- [ ] Unsupported or unrepresentable values fail planning before writes; projects cannot self-assert migration support.
- [ ] The journal and plan schemas are strict, versioned, canonical, digest-bound, project-contained, resumable, and explicit about cooperative freeze and non-atomic stages.
- [ ] Stage approval, pre-cutover cleanup, post-cutover roll-forward, deterministic configuration cutover, and tombstone rules are specified.
- [ ] The complete current backend-pair matrix and exclusions are documented and verifier-enforced.

## Blocked by

None.

## Out of scope

Adapter implementation, the user-facing skill, reclassification, free-form link rewriting, and Things.

## Comments
## Resolution

Specified the strict one-route migration contract established by ARP-0010. Added normative version-1 JSON schemas for complete provider-neutral snapshots, canonical digest-bound plans, and guarded resumable journals. The specification defines active/history inventory, exact content hashes, opaque references/revisions, lifecycle state, comments, labels, assignees, timestamps, structured relationships, deterministic ordering, semantic-lossless canonical provenance, provider metadata classifications, stable non-issue IDs, mapped issue IDs, cooperative freeze, three separately approved stages, pre-cutover cleanup, irreversible post-cutover roll-forward, deterministic configuration cutover, source tombstones/archive, and completion invariants. Upgraded immutable adapter capability declarations to schema 2 with separate issue/non-issue migration operation lists (`export-history`, `import`, `verify`, `retire`); all remain empty until adapter conformance lands, so this specification grants no unsupported capability. Added verifier helpers that require complete source/destination role operations, reject same-type moves and Bear issues, and enforce the full directional local/GitHub/Bear target matrix with capability-complete fixtures. Updated the portable contract, active routing specification, backend guidance, ARP-0009 refinement note, changelog, bundled declarations, and manifest. Added strict schema, matrix, exclusion, immutable declaration, and implicit-migration regressions. `scripts/verify.sh` passes with 169 tests.
