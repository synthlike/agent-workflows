---
id: ISSUE-0047
title: "Implement the Bear non-issue record adapter"
kind: "implementation"
status: resolved
created: 2026-08-25
assignee: "pi"
parent: "ISSUE-0043-add-bear-for-non-issue-record-routing.md"
blocked_by:
  - "ISSUE-0046-configure-and-preflight-scoped-bear-backends.md"
labels: ["bear","record-routing"]
---
# Implement the Bear non-issue record adapter

## Parent

Add Bear for non-issue record routing

## What to build

Implement every common record operation for all eleven non-issue semantic types through the scoped Bear MCP transport.

## Acceptance criteria

- [ ] Create, read, list/search, revision-gated update, metadata-only archive, and reference rendering pass the shared record conformance suite for all eleven types.
- [ ] Managed notes use the canonical metadata envelope followed by canonical content and carry both the workspace root tag and configured nested route tag.
- [ ] Portable revisions wrap Bear `baseHash`; stale writes fail without mutation.
- [ ] Semantic IDs allocate inside create, include scoped archived records when detecting collisions, recheck before creation, and fail safely on observed duplicates.
- [ ] Archive retains direct readability while excluding records from normal list/search.
- [ ] References preserve backend instance, native Bear note ID, title, and a documented stable deep link when available; malformed references fail safely.
- [ ] Provider and protocol failures map to stable portable errors without partial mutation.
- [ ] The adapter exposes no issue operations.

## Blocked by

Scoped Bear configuration and preflight.

## Out of scope

Bear issue semantics, atomic allocation across simultaneous clients, migration, synchronization, and live-test requirements.

## Comments
## Resolution

Implemented the complete Bear non-issue record adapter for all eleven supported semantic types. Managed Bear notes now preserve canonical semantic metadata, a provider-owned title heading, deterministic workspace and nested-route hashtags, metadata-only archive state, native note-ID references, and opaque `bear-base-hash` revisions. Create allocates and immediately rechecks semantic IDs across active and metadata-archived notes; read and paginated list/search parse complete managed records; update and archive require the latest whole-note hash and rely on MCP `baseHash` to close the final race. Every mutation re-reads for the next revision. The adapter rejects Bear `issues`, malformed notes/destinations/references, duplicate owners, stale writes, attachments that a whole-note overwrite could remove, and provider/protocol failures without partial adapter mutation. Added portable CLI operations and reference rendering that does not launch Bear. Bear's immutable declaration now advertises the complete common record contract. Shared and Bear-specific tests cover every record type, operations, pagination, framing, collisions including archived records, external and in-flight races, stable encoded links, malformed state, portable errors, and the absence of an issue extension. Updated backend and configuration documentation. A live read-only preflight still passes; no live Bear record mutation was performed. `scripts/verify.sh` passes with 127 tests.
