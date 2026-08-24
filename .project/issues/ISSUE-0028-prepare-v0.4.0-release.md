---
id: ISSUE-0028
title: Prepare the v0.4.0 release
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent:
blocked_by: []
labels: [v0.4, release]
---

# Prepare the v0.4.0 release

## What to build

Turn the completed schema and maintenance cleanup into a deterministic v0.4.0 release with aligned changelog, documentation, manifest, real fresh-adoption evidence, release asset, commit, and annotated tag.

## Acceptance criteria

- [x] Schema 2 is the sole supported configuration and all cleanup issues are resolved.
- [x] `CHANGELOG.md` contains a dated `0.4.0` release entry.
- [x] Release metadata, source inventory, documentation, dependency table, and manifest agree on v0.4.0 and all 20 skills.
- [x] The real `skills@latest` and Pi smoke test passes using the metadata-derived bundle name.
- [x] The deterministic `agent-workflows-v0.4.0.tar.gz` validates and its SHA-256 is recorded.
- [x] All structural, unit, fixture, installed, release, syntax, and documentation-link checks pass from a clean tree.
- [x] A release commit and annotated `v0.4.0` tag are created after explicit approval.

## Blocked by

None.

## Out of scope

- New workflow behavior.
- Automated update, rollback, recovery, migration, or self-update behavior.
- Hosting-service publication without explicit approval.

## Comments

2026-08-24 — synthlike: `skills@latest` 1.5.23 copied only `configure-project` and `frame-product-problem` into a temporary Pi consumer. The smoke script derived `v0.4.0` from release metadata, completed dependency closure, confirmed Pi discovery, wrote schema 2, verified without a source checkout, and preserved lazy ownership. `/tmp/agent-workflows-v0.4.0.tar.gz` validates with SHA-256 `dd64ea9ef78ab5308553a2d22db9af0f1beaa28418e2f14c6cdf2164007edbe4`. All 50 grouped tests and repository checks pass before the release commit.

## Resolution

Resolved on 2026-08-24 after explicit release approval. v0.4.0 removes active schema-1 compatibility, retains schema 2 as the sole supported configuration, and reduces release-documentation, smoke-test, verification, and test-fixture churn without changing the 20-skill workflow set. The real `skills@latest` and Pi smoke test passes, all 50 grouped tests and repository checks pass, and `/tmp/agent-workflows-v0.4.0.tar.gz` validates with SHA-256 `dd64ea9ef78ab5308553a2d22db9af0f1beaa28418e2f14c6cdf2164007edbe4`. The approved release commit is tagged `v0.4.0`.
