---
id: ISSUE-0052
title: "Bundle canonical consumer guidance templates"
kind: "implementation"
status: open
created: 2026-08-25
assignee: 
parent: "ISSUE-0050-streamline-deterministic-consumer-configuration.md"
blocked_by:
labels: ["lifecycle","configuration"]
---
# Bundle canonical consumer guidance templates

## Parent

Streamline deterministic consumer configuration

## What to build

Provide canonical distribution-managed templates that make configuration and guidance generation deterministic while preserving explicit project-owned content boundaries.

## Acceptance criteria

- [ ] Bundled templates cover schema-3 `workflows.yaml`, `docs/agents/workflows.md`, `docs/agents/records.md`, and the root agent-guidance section.
- [ ] Workflow guidance always contains the literal canonical instruction to read `docs/agents/records.md` for record routing and operations.
- [ ] Templates render every route explicitly, include exact used backend assets, preserve authority/documentation policy, and describe disabled-route and approval boundaries.
- [ ] Rendering is byte-for-byte deterministic for identical normalized inputs.
- [ ] Root guidance uses an unambiguous managed section and preserves all unrelated existing `AGENTS.md` or equivalent bytes.
- [ ] Generated template output passes installed `verify-consumer` without hand repair.
- [ ] Release manifest integrity covers every template.

## Blocked by

None.

## Out of scope

Applying generated files, replacing skill directories, provider provisioning, and record migration.

## Comments


## Resolution
