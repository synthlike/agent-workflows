---
id: ISSUE-0061
title: "Implement GitHub migration operations"
kind: "implementation"
status: cancelled
created: 2026-08-25
assignee: 
parent: "ISSUE-0058-implement-strict-cross-backend-record-migration.md"
blocked_by:
  - "ISSUE-0059-specify-portable-migration-snapshots-and-capabilities.md"
labels: ["migration","github"]
---
# Implement GitHub migration operations

## Parent

Implement strict cross-backend record migration

## What to build

Implement complete issue and non-issue migration export, semantic-lossless import, verification, collision handling, provenance, and retirement for GitHub under explicit repository/login identity.

## Acceptance criteria

- [ ] Export deterministically enumerates active and historical managed records/issues, paginates comments and relationships, and binds current provider revisions.
- [ ] Import is idempotent and collision-safe, preserves exact content and portable meaning, recreates structured relationships, and represents non-native authors, timestamps, assignees, states, or source IDs canonically.
- [ ] Non-issue IDs remain stable; provider-assigned issue IDs produce durable opaque source/destination mappings.
- [ ] Retirement archives non-issues through managed state, cancels active issues with tombstones, and adds provenance to terminal issues without changing terminal state.
- [ ] Identity, permission, managed-label, stale-state, rate-limit, partial-failure, and shared conformance scenarios fail safely without silent loss.

## Blocked by

Portable migration specification and capabilities.

## Out of scope

Local Markdown, Bear, label provisioning without separate approval, and configuration cutover.

## Comments
## Resolution

Cancelled in the core repository after ARP-0011 externalized record migration as a possible separate optional project. The implementation is not part of v0.5.0 or assigned to a later core release. Historical commits and issue context are retained for future reference.
