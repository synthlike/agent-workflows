---
id: ISSUE-0022
title: Validate and prepare v0.3.0
kind: task
status: open
created: 2026-08-24
assignee:
parent: ../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md
blocked_by:
  - ISSUE-0021-integrate-v0.3-workflow-set.md
labels: [v0.3, release]
---

# Validate and prepare v0.3.0

## Parent

[v0.3 project-foundation and feedback workflows](../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md)

## What to build

Validate the complete v0.3 workflow release through real fresh-project adoption and produce a deterministic, documented, tagged v0.3.0 release candidate.

## Acceptance criteria

- [ ] A real Agent Skills-compatible installer smoke test begins with an intentionally incomplete selection containing at least one new workflow.
- [ ] Closure completion, schema-2 inventory, harness discovery, installed verification without a source checkout, and lazy project ownership all pass.
- [ ] Representative contract scenarios for all six new workflows pass without unauthorized writes or authority violations.
- [ ] Release metadata, manifest, dependency table, documentation, examples, changelog, and bundle agree on v0.3.0 and all 19 skills.
- [ ] The deterministic `agent-workflows-v0.3.0.tar.gz` validates and its SHA-256 is recorded.
- [ ] All structural, unit, fixture, integration, installed, release, syntax, and documentation-link checks pass from a clean tree.
- [ ] A release commit and annotated `v0.3.0` tag are created after explicit approval.

## Blocked by

- [Integrate and document the v0.3 workflow set](ISSUE-0021-integrate-v0.3-workflow-set.md)

## Out of scope

- Hosting-service publication without explicit approval.
- Automated update, rollback, recovery, migration, or self-update behavior.
- Expanding v0.3 beyond the accepted six workflows.
