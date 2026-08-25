---
id: ISSUE-0022
title: Validate and prepare v0.3.0
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent: ../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md
blocked_by:
  - ISSUE-0021-integrate-v0.3-workflow-set.md
  - ISSUE-0023-rename-wayfinder-labels.md
  - ISSUE-0024-add-product-problem-framing-to-v0.3-scope.md
  - ISSUE-0025-implement-frame-product-problem.md
labels: [v0.3, release]
---

# Validate and prepare v0.3.0

## Parent

[v0.3 project-foundation and feedback workflows](../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md)

## What to build

Validate the complete v0.3 workflow release through real fresh-project adoption and produce a deterministic, documented, tagged v0.3.0 release candidate.

## Acceptance criteria

- [x] A real Agent Skills-compatible installer smoke test begins with an intentionally incomplete selection containing at least one new workflow.
- [x] Closure completion, schema-2 inventory, harness discovery, installed verification without a source checkout, and lazy project ownership all pass.
- [x] Representative contract scenarios for all seven new workflows pass without unauthorized writes or authority violations.
- [x] Release metadata, manifest, dependency table, documentation, examples, changelog, and bundle agree on v0.3.0 and all 20 skills.
- [x] The deterministic `agent-workflows-v0.3.0.tar.gz` validates and its SHA-256 is recorded.
- [x] All structural, unit, fixture, integration, installed, release, syntax, and documentation-link checks pass from a clean tree.
- [x] A release commit and annotated `v0.3.0` tag are created after explicit approval.

## Blocked by

- [Integrate and document the v0.3 workflow set](ISSUE-0021-integrate-v0.3-workflow-set.md)
- [Rename legacy Wayfinder labels](ISSUE-0023-rename-wayfinder-labels.md)
- [Add product-problem framing to v0.3 scope](ISSUE-0024-add-product-problem-framing-to-v0.3-scope.md)
- [Implement frame-product-problem](ISSUE-0025-implement-frame-product-problem.md)

## Out of scope

- Hosting-service publication without explicit approval.
- Automated update, rollback, recovery, migration, or self-update behavior.
- Expanding v0.3 beyond the accepted seven workflows.

## Comments

2026-08-24 — synthlike: `skills@latest` 1.5.23 copied only `configure-workflows` and `frame-product-problem` into a temporary Pi consumer. Installed lifecycle planning added the complete closure, Pi's SDK confirmed discovery, schema-2 setup verified outside the source checkout, and lazy-directory checks passed. After the product-framing scope amendment, the smoke test passed again with the twentieth skill and the final candidate `/tmp/agent-workflows-v0.3.0.tar.gz` validates with SHA-256 `d0646fa11f888101c54d61401f13c007f7588f4958be1c00c954f0f2b3fd16d4`. All 80 tests and repository checks pass before the release commit.

## Resolution

Resolved on 2026-08-24 after explicit release approval. v0.3.0 distributes 20 skills, including seven new project-foundation and feedback workflows. The real `skills@latest` and Pi smoke test completed the dependency closure from only `configure-workflows` and `frame-product-problem`, confirmed discovery, wrote schema 2, verified without a source checkout, and preserved lazy project ownership. All 80 tests and repository checks pass. The deterministic asset `/tmp/agent-workflows-v0.3.0.tar.gz` validates with SHA-256 `d0646fa11f888101c54d61401f13c007f7588f4958be1c00c954f0f2b3fd16d4`, and the approved release commit is tagged `v0.3.0`.
