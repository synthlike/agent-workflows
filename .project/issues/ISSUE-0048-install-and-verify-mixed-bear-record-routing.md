---
id: ISSUE-0048
title: "Install and verify mixed Bear record routing"
kind: "implementation"
status: open
created: 2026-08-25
assignee: 
parent: "ISSUE-0043-add-bear-for-non-issue-record-routing.md"
blocked_by:
  - "ISSUE-0047-implement-the-bear-non-issue-record-adapter.md"
labels: ["bear","record-routing"]
---
# Install and verify mixed Bear record routing

## Parent

Add Bear for non-issue record routing

## What to build

Generate complete consumer configuration, guidance, and helpers for projects that route non-issue records to Bear while retaining a complete issue backend.

## Acceptance criteria

- [ ] Bear-plus-local and Bear-plus-GitHub installed-consumer scenarios define all twelve explicit routes and pass verification.
- [ ] Generated assets include one shared contract and exactly the helpers/guidance required by routed backend types, with Bear instances sharing one helper.
- [ ] Generated record guidance describes Bear workspace-relative destinations, opaque revisions and references, disabled-route behavior, and approval boundaries.
- [ ] Installed verification rejects missing, modified, stale, or unexpected Bear assets and unsupported Bear `issues` routes.
- [ ] Source-checkout-free verification and helper entrypoints pass with deterministic mocked MCP.
- [ ] Tests cover disabled routes, stale writes, collisions, malformed managed notes and references, cross-backend links, and incomplete capabilities without backend mutation.

## Blocked by

The conforming Bear non-issue adapter.

## Out of scope

Things-backed issues, Bear-backed issues, and migration of existing records.

## Comments


## Resolution
