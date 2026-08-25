---
id: ISSUE-0049
title: "Document and smoke-test Bear routing"
kind: "implementation"
status: resolved
created: 2026-08-25
assignee: "pi"
parent: "ISSUE-0043-add-bear-for-non-issue-record-routing.md"
blocked_by:
  - "ISSUE-0048-install-and-verify-mixed-bear-record-routing.md"
labels: ["bear","record-routing"]
---
# Document and smoke-test Bear routing

## Parent

Add Bear for non-issue record routing

## What to build

Finish release-ready Bear guidance and provide an opt-in live verification path without making Bear installation or database mutation part of normal repository verification.

## Acceptance criteria

- [ ] User and backend documentation describes configuration, preflight, supported routes, managed metadata, archive behavior, revisions, references, concurrency boundaries, and recovery-safe failure behavior.
- [ ] Documentation states that Bear does not support `issues` and shows mixed routing with a complete issue backend.
- [ ] A read-only live preflight can run when Bear is installed and is skipped cleanly otherwise.
- [ ] An optional live CRUD smoke test requires explicit approval, uses a disposable workspace, verifies create/read/search/update/archive, and reports cleanup state.
- [ ] The normal release suite uses mocks, neither requires Bear nor mutates a Bear database, and passes completely.

## Blocked by

Installed mixed Bear routing.

## Out of scope

Running live CRUD without separate approval, Bear issue semantics, Things implementation, and record migration.

## Comments
## Resolution

Completed release-ready Bear guidance and optional live verification paths. Canonical and bundled backend documentation now covers explicit command/workspace and relative-tag configuration, complete mixed routing with `issues` on local Markdown, all eleven supported routes, exact managed note framing, metadata-only retained archive, opaque `bear-base-hash` revisions, native note-ID references, attachment and encrypted-note boundaries, stale-write behavior, non-atomic create allocation, ambiguous transport/process recovery, and retained cleanup. Added `scripts/smoke-bear-preflight.sh`: it invokes only the adapter's zero-tool read-only preflight, skips with explicit JSON when Bear is unavailable, and can require availability. Added `scripts/smoke-bear-crud.sh`: it refuses mutation without exact `BEAR_CRUD_APPROVED=YES`, requires a unique `agent-workflows-smoke/*` workspace, and verifies create/read/query search/update/stale rejection/archive/active-search exclusion before reporting the metadata-archived retained note and workspace. Normal verification only syntax-checks both live scripts and continues to use mocked MCP; regressions verify clean skip, required-command failure, approval/workspace refusal before executable invocation, CRUD contract presence, exact bundled guidance, and no live execution in the normal suite. Updated user-facing record/configuration guidance and changelog. The approved read-only live preflight passed against Bear CLI `2.9.3 (14672)`; live CRUD was not run because no separate mutation approval was requested. `scripts/verify.sh` passes with 164 tests.
