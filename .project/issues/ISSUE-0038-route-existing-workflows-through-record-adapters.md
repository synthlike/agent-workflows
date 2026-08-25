---
id: ISSUE-0038
title: Route existing workflows through record adapters
kind: task
status: resolved
created: 2026-08-25
assignee: pi
parent: ../../docs/specifications/record-routing-and-backend-contracts.md
blocked_by:
  - ISSUE-0037-configure-and-verify-an-all-local-schema-3-consumer.md
labels: [record-routing, phase-1]
---

# Route existing workflows through record adapters

## Question or work

Make persistence instructions in every existing skill provider-neutral through semantic record routes and generated adapter guidance.

## Acceptance criteria

- Skills use semantic record keys and adapter operations.
- Skills no longer construct paths, provider IDs, tags, labels, or links.
- Disabled-route and approval behavior remains intact.
- Initiative maps, findings, reviews, and closure summaries retain their agreed boundaries.
- Distribution integrity and dependency verification pass.

## Parent

[Record routing and backend conformance](../../docs/specifications/record-routing-and-backend-contracts.md)

## Comments

## Resolution

Routed all nineteen existing operational skills through `.agents/workflows.yaml`, `docs/agents/records.md`, semantic record keys, and portable adapter operations. Skills now use adapter allocation, revision-gated updates, issue lifecycle operations, opaque structured references, and destination-adapter rendering without constructing provider paths, identifiers, labels, tags, or links. Disabled-route and mutation-approval boundaries remain explicit for every workflow. Initiative maps and decision tickets remain issue structures; failure findings, regression results, implementation reviews, and closure summaries update requesting issues or parents rather than creating new authority types; durable prototype metadata and conclusions use `prototypes` while executable files may remain temporary or external. Added portable structured-reference parsing and local Markdown rendering, bundled the updated helper, and added cross-skill conformance tests for routes, provider neutrality, and authority boundaries. `scripts/verify.sh` passes with 75 tests.
