---
id: ISSUE-0043
title: "Add Bear for non-issue record routing"
kind: "initiative"
status: open
created: 2026-08-25
assignee: 
parent: 
blocked_by:
labels: ["bear","record-routing"]
---
# Add Bear for non-issue record routing

## Destination

Projects can route any of the eleven non-issue semantic record types to a scoped Bear workspace while routing `issues` to another complete backend such as local Markdown, GitHub, or a future Things adapter.

## Notes

Follow ARP-0009, the portable record contract, and the existing Bear MCP scoping research. Bear capabilities are adapter-owned and verifier-enforced. The helper launches an explicitly configured `bearcli` executable over scoped MCP stdio. Managed notes use canonical metadata, Bear `baseHash` revisions, workspace-relative route tags, metadata-only archive, and stable note-ID links when documented.

Normal verification uses deterministic mocked MCP. Live preflight is read-only. Any live CRUD smoke test uses a disposable workspace and requires separate approval.

## Decisions so far

- Declare backend record capabilities explicitly — immutable adapter-owned declarations now distinguish complete non-issue and issue operation contracts.
- Verify the Bear MCP record contract — scoped stdio MCP exposes the required paginated note operations, whole-note hashes, native IDs, and deterministic preflight surface.
- Configure and preflight scoped Bear backends — explicit command/workspace configuration and zero-write MCP inspection establish provider capability before routes are approved.
- Implement the Bear non-issue record adapter — all eleven note routes now satisfy the common contract with scoped tags, whole-note revisions, managed archive state, and native references.
- Bear supports the eleven non-issue record types, not `issues`.
- Backend adapters declare supported record types and operations; projects do not self-assert capabilities.
- Backend instances configure explicit `command` and `workspace`; destinations configure workspace-relative `tag`.
- Managed notes reuse the canonical record metadata envelope and preserve native note IDs only in opaque references.
- Revisions wrap Bear `baseHash`; archive is metadata-only.
- Identifier allocation rechecks scoped managed notes but remains non-atomic across simultaneous clients.

## Execution plan

Independent frontier:

- Declare backend record capabilities explicitly
- Verify the Bear MCP record contract

Dependent slices:

- Configure and preflight scoped Bear backends
- Implement the Bear non-issue record adapter
- Install and verify mixed Bear record routing
- Document and smoke-test Bear routing

## Not yet specified

None.

## Out of scope

- Bear issue lifecycle, dependencies, claims, comments, cancellation, or frontier traversal.
- Things implementation.
- Existing-record migration, mirroring, synchronization, or route-change movement.
- Mandatory Bear installation or live mutation in the release suite.

## Comments


## Resolution
