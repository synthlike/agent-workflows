---
id: ISSUE-0045
title: "Verify the Bear MCP record contract"
kind: "research"
status: open
created: 2026-08-25
assignee: 
parent: "ISSUE-0043-add-bear-for-non-issue-record-routing.md"
blocked_by:
labels: ["bear","record-routing"]
---
# Verify the Bear MCP record contract

## Parent

Add Bear for non-issue record routing

## What to establish

Use current primary Bear documentation and local `bearcli` help to establish the exact MCP protocol and tool contract required by a portable non-issue record adapter.

## Acceptance criteria

- [ ] Record MCP initialization, tool names, input/output schemas, errors, and availability requirements for scoped search, read, create, whole-note overwrite with `baseHash`, and tags.
- [ ] Verify `--only-tags` read/write behavior, automatic workspace-tag injection, nested-tag behavior, note identifiers, search completeness or pagination, and stale-write semantics.
- [ ] Verify the documented stable note-ID deep-link format or record that no suitable format exists.
- [ ] Resolve whether managed metadata and metadata-only archive remain readable through the scoped server.
- [ ] Update the existing Bear research record with cited facts, bounded uncertainties, and implementation consequences.
- [ ] Perform no Bear mutation.

## Blocked by

None.

## Out of scope

Adapter implementation, live CRUD, Bear issue semantics, and Things.

## Comments


## Resolution
