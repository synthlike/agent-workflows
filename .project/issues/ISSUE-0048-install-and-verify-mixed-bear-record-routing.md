---
id: ISSUE-0048
title: "Install and verify mixed Bear record routing"
kind: "implementation"
status: resolved
created: 2026-08-25
assignee: "pi"
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

Added complete Bear-plus-local and Bear-plus-GitHub installed-consumer profiles with all twelve explicit routes: `issues` remains on a complete issue backend while all eleven non-issue routes use workspace-relative Bear tags. Generated consumers now receive exactly one shared contract and one guidance/helper pair per used backend type; multiple Bear instances share the same pair and unused Bear instances generate nothing. Added a complete Bear-plus-local configuration example and expanded `configure-workflows` recommendations and user guidance. Installed verification now proves successful Bear profiles, exact guidance, disabled-route boundaries, unsupported Bear `issues`, incomplete capability rejection before mutation, missing/modified/unexpected Bear asset rejection, Bear/local/GitHub cross-reference rendering, and source-checkout-free lifecycle operation. The bundled Bear helper also completes deterministic mocked preflight from an isolated installed directory without source access. Existing shared and Bear-specific suites cover stale writes, collisions including archived records, malformed managed notes/references, pagination, and portable failures. No live Bear mutation occurs in verification. `scripts/verify.sh` passes with 133 tests.
