<!-- agent-workflows-record
{"archived":false,"created":"2026-08-27T18:53:44Z","id":"ARP-0011","modified":"2026-08-27T18:53:44Z","record_type":"arps","title":"Keep record migration outside the core distribution"}
-->
---
id: ARP-0011
title: Keep record migration outside the core distribution
status: accepted
date: 2026-08-27
supersedes:
  - ARP-0010
superseded_by:
related_rfcs: []
---

# Keep record migration outside the core distribution

## Context

Strict cross-backend migration grew into a separate high-risk subsystem: provider-specific export and import, portable snapshots, fidelity classification, resumable journals, staged approvals, route cutover, source retirement, and pairwise recovery testing. Its remaining work dominated the `v0.5.0` release and introduced issue-content and runtime-contract questions unrelated to ordinary workflow configuration and record operation.

The core distribution is intended to define semantic workflows, configure explicit record routes, and operate records through stable backends. Most consumers do not need cross-provider migration during normal use, but installing the complete distribution would require them to receive and verify all migration machinery.

## Decision

Agent Workflows will not implement or distribute cross-backend record migration in the core repository. Ordinary configuration and route changes remain strictly non-migrating.

The partial migration implementation, capabilities, machine schemas, active specification, and release claims are removed from `v0.5.0`. The migration initiative and unfinished implementation issues are cancelled as externalized rather than completed. Historical commits and decision records remain available; this ARP supersedes ARP-0010 instead of deleting it.

A future optional project may provide migration skills and Python helpers with its own release cadence, dependencies, approval model, provider adapters, journals, and conformance matrix. It should integrate through versioned data and command boundaries: read supported Agent Workflows configuration, preserve semantic record contracts, avoid modifying installed skills, and use installed deterministic configuration plan/apply for any route cutover. No future release number or implementation commitment is made here.

## Rationale

Separating exceptional migration from normal workflow operation keeps the complete core installation small and cohesive. It prevents unfinished cross-provider semantics from delaying schema-3 routing, Bear support, and deterministic configuration. An optional project can evolve safety and provider dependencies independently without making every consumer install a large maintenance subsystem.

Keeping historical artifacts and recording supersession preserves the reason for the change without presenting abandoned behavior as active architecture.

## Consequences

- `v0.5.0` contains schema-3 routing, Local Markdown, GitHub, Bear non-issue support, corrected discovery, canonical templates, and deterministic configuration plan/apply, but no supported record migration.
- Core backend capability declarations return to ordinary record and issue operations only.
- The strict migration specification and machine schemas are removed from active core documentation and distribution assets.
- ARP-0010 remains as a superseded historical decision.
- Migration issues remain as retained project history with explicit externalized outcomes.
- Route changes never imply moving, copying, rewriting, or retiring existing records.
- A future migration project must define and test compatibility with specific Agent Workflows versions rather than importing private Python implementation details.
