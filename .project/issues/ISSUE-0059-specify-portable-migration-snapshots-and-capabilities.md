---
id: ISSUE-0059
title: "Specify portable migration snapshots and capabilities"
kind: "implementation"
status: open
created: 2026-08-25
assignee: 
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
