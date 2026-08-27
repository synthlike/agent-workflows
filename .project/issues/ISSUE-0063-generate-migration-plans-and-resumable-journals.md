---
id: ISSUE-0063
title: "Generate migration plans and resumable journals"
kind: "implementation"
status: cancelled
created: 2026-08-25
assignee: 
parent: "ISSUE-0058-implement-strict-cross-backend-record-migration.md"
blocked_by:
  - "ISSUE-0059-specify-portable-migration-snapshots-and-capabilities.md"
labels: ["migration","lifecycle"]
---
# Generate migration plans and resumable journals

## Parent

Implement strict cross-backend record migration

## What to build

Add source-checkout-free deterministic planning for one strict route and an approved project-contained journal that can resume the non-atomic migration saga safely.

## Acceptance criteria

- [ ] Strict versioned intent selects one route, configured source, capability-compatible destination, approved journal path, and provider identity evidence.
- [ ] The plan inventories active/history snapshots, source revisions, destination collision/absence state, normalized transformations/provenance, relationship ordering, copy verification, configuration cutover intent, retirement operations, and lazy/created paths.
- [ ] Plan identity is canonical `sha256`; identical state and intent produce identical bytes.
- [ ] Planning performs no mutation and rejects stale, unsupported, lossy, escaping, colliding, incomplete, or provider-mismatched input.
- [ ] Journal creation requires approval, binds the plan digest, and records idempotent stage transitions, mappings, evidence, failures, freeze acknowledgement, and recovery direction.
- [ ] Resume validates journal, plan, installation, route, provider identity, and all completed evidence before continuing.

## Blocked by

Portable migration specification and capabilities.

## Out of scope

Destination writes, route cutover, retirement, and the skill interview.

## Comments
## Resolution

Cancelled in the core repository after ARP-0011 externalized record migration as a possible separate optional project. The implementation is not part of v0.5.0 or assigned to a later core release. Historical commits and issue context are retained for future reference.
