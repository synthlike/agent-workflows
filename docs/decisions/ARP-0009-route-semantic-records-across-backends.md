---
id: ARP-0009
title: Route semantic records across backends
status: accepted
date: 2026-08-25
supersedes:
  - ARP-0008
superseded_by:
related_rfcs:
  - ../rfcs/RFC-0006-route-record-types-across-storage-backends.md
---

# Route semantic records across backends

## Context

Schema 2 separates one issue backend from repository-path artifact settings. That model cannot express local Markdown or GitHub for every record, mixed GitHub and local routing, Things for issues with Bear for supporting records, or Bear for every record. ARP-0008 additionally fixes authoritative RFCs, ARPs, specifications, domain models, and technical baselines in Git, even though authority belongs to semantic record type rather than storage location.

## Decision

Schema 3 replaces schema 2 without compatibility or migration support. It defines named backend instances and explicit routes for `issues`, `domain`, `arps`, `rfcs`, `specs`, `meetings`, `research`, `questionnaires`, `technical_baselines`, `problem_framing`, `prototypes`, and `handoffs`. Every route retains `enabled`, `backend`, and a complete typed `destination`.

A backend may receive a route only when it implements the complete required record contract and, for `issues`, the complete issue contract. Adapters own stale-write protection, create-time identifier allocation, stable structured references, provider rendering, and conformance tests. Authority follows record type, not backend.

Phase 1 implements schema 3 and backend-neutral contracts with local Markdown as the reference adapter and GitHub as the second adapter. Bear MCP and Things MCP follow separately. Bear uses a project-level `workspace` tag and nested per-record `tag` destinations. GitHub separates `workflow:record:*` labels from `workflow:issue:*` kinds and closes non-issue storage records as completed after publication.

This decision supersedes ARP-0008. It retains ARP-0008's explicit GitHub login, native sub-issues and dependencies, deterministic pagination, close-reason distinction, reviewed label provisioning, and documented claim-race boundary, while replacing its repository-only authority boundary and one-dimensional labels.

## Rationale

Named backends avoid repeating credentials and provider identity. Explicit routes make mixed persistence auditable and avoid hidden profile inheritance. Shared semantic contracts keep workflows provider-independent and prevent unsupported operations from silently degrading. Phased implementation establishes portable behavior before adding MCP providers with materially different storage and concurrency semantics.

## Consequences

- Schema 2 and `docs/agents/issue-tracker.md` are removed atomically in phase 1.
- `docs/agents/records.md` and one shared guidance/helper pair per used backend type replace issue-only generated guidance.
- `specs` replaces the `specifications` configuration key and default destination name; `author-specification` remains unchanged.
- Existing project configuration, paths, GitHub labels, helpers, documentation, fixtures, and verification are rewritten without migration support.
- Cross-backend synchronization, mirroring, route-change migration, and distributed transactions remain unsupported.
- Bear and Things cannot be advertised for a route until their adapters pass the common contract suite.
