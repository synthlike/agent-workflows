---
id: ISSUE-0062
title: "Implement Bear migration operations"
kind: "implementation"
status: cancelled
created: 2026-08-25
assignee: 
parent: "ISSUE-0058-implement-strict-cross-backend-record-migration.md"
blocked_by:
  - "ISSUE-0059-specify-portable-migration-snapshots-and-capabilities.md"
labels: ["migration","bear"]
---
# Implement Bear migration operations

## Parent

Implement strict cross-backend record migration

## What to build

Implement complete historical export, semantic-lossless import, verification, collision handling, provenance, and metadata retirement for all eleven Bear-supported non-issue routes.

## Acceptance criteria

- [ ] Export enumerates active and metadata-archived managed notes under the exact scoped workspace/route and binds whole-note hashes.
- [ ] Import is idempotent, collision-safe, preserves semantic IDs and exact canonical content, writes valid managed framing/tags, and records representable provenance.
- [ ] Verification detects malformed metadata, missing tags, encrypted content, attachments, stale hashes, ambiguous creates, and unrepresentable values before cutover.
- [ ] Retirement uses hash-gated metadata archive and retains native notes and stable references.
- [ ] Mocked MCP conformance covers pagination, retries, partial failure, resume, and all capability-compatible local/GitHub pair directions without live mutation.

## Blocked by

Portable migration specification and capabilities.

## Out of scope

`issues`, native deletion, Local Markdown, GitHub, and live CRUD without separate approval.

## Comments
## Resolution

Cancelled in the core repository after ARP-0011 externalized record migration as a possible separate optional project. The implementation is not part of v0.5.0 or assigned to a later core release. Historical commits and issue context are retained for future reference.
