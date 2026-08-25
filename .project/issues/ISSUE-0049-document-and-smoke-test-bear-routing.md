---
id: ISSUE-0049
title: "Document and smoke-test Bear routing"
kind: "implementation"
status: open
created: 2026-08-25
assignee: 
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
