---
id: ISSUE-0046
title: "Configure and preflight scoped Bear backends"
kind: "implementation"
status: resolved
created: 2026-08-25
assignee: "pi"
parent: "ISSUE-0043-add-bear-for-non-issue-record-routing.md"
blocked_by:
  - "ISSUE-0044-declare-backend-record-capabilities-explicitly.md"
  - "ISSUE-0045-verify-the-bear-mcp-record-contract.md"
labels: ["bear","record-routing"]
---
# Configure and preflight scoped Bear backends

## Parent

Add Bear for non-issue record routing

## What to build

Let a project configure a named Bear backend with an explicit `bearcli` command and workspace, route supported non-issue records to workspace-relative tags, and complete a read-only capability preflight over scoped MCP stdio.

## Acceptance criteria

- [ ] Bear backend instances require exactly `type`, absolute executable `command`, and non-empty `workspace` fields.
- [ ] Bear destinations require exactly one workspace-relative `tag` and reject leading `#` or `/`, workspace repetition, empty segments, and escape-like forms.
- [ ] The helper launches the configured command as `mcp-server --only-tags WORKSPACE`, performs protocol initialization, and reports identity and required tool capabilities without creating or changing notes or tags.
- [ ] Configuration cannot route `issues` to Bear and cannot approve Bear routes when preflight lacks a required common operation.
- [ ] Configuration and provisioning remain review- and approval-gated, with no harness-specific MCP registration.
- [ ] Deterministic tests cover command failure, protocol errors, missing tools, malformed fields, and zero-write preflight.

## Blocked by

The Bear MCP contract research and canonical capability declarations.

## Out of scope

Record CRUD, live mutation, Bear issue support, and Things.

## Comments
## Resolution

Added explicit Bear backend configuration with required absolute `command` and scoped `workspace`, strict workspace-relative destination tags, and rejection of Bear `issues` or any Bear route whose immutable adapter declaration lacks required operations. Added a bundled `bear.py` helper that launches exactly `COMMAND mcp-server --only-tags WORKSPACE`, initializes MCP 2025-06-18, validates the `bearcli` identity and echoed scope, and verifies required create/read/list/search/`baseHash` overwrite/tag tool schemas and annotations using only `initialize` and `tools/list`. Bear currently declares the eleven intended non-issue types but no completed operations, so provider preflight can succeed while route approval remains safely blocked until CRUD lands. Updated configuration workflow instructions, generated-asset verification, backend guidance, lifecycle documentation, and changelog. Deterministic tests cover malformed transport, identity, scope, protocol, missing tools, annotations, command availability, backend fields, destination tags, zero-write preflight, and unused assets. A live read-only preflight passed against Bear CLI 2.9.3. `scripts/verify.sh` passes with 111 tests.
