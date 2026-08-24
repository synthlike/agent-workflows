---
id: ISSUE-0027
title: Reduce repository maintenance churn
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent:
blocked_by:
  - ISSUE-0026-remove-schema-1-support.md
labels: [v0.4, cleanup, documentation, tests]
---

# Reduce repository maintenance churn

## What to build

Reduce repeated release edits and test boilerplate without weakening self-contained skills, deterministic distribution, artifact history, or verification coverage.

## Acceptance criteria

- [x] Operational lifecycle documentation uses release-neutral language and `vMAJOR.MINOR.PATCH` placeholders where behavior is not version-specific.
- [x] The fresh-install smoke test derives the current release version and bundle name from authoritative release metadata or the installed manifest instead of embedding a version.
- [x] Release verification derives current contract links, skill inventory, version, and changelog expectations from authoritative metadata where practical instead of accumulating release-specific string lists.
- [x] Shared consumer-fixture construction removes repeated schema-2 configuration, guidance, skill-copy, and inventory setup from tests while preserving scenario readability.
- [x] v0.3 skill-contract checks use table-driven helpers where repeated assertions have the same semantics, without reducing contract coverage.
- [x] `.gitignore` excludes Python bytecode and caches, test caches, and generated `dist/` release assets.
- [x] Bundled backend adapters, configured consumer guidance, self-contained skill instructions, historical artifacts, and generated manifest data remain intact rather than being deduplicated unsafely.
- [x] All structural, unit, fixture, installed, release, syntax, and documentation-link checks pass.

## Blocked by

- [Remove schema-1 support](ISSUE-0026-remove-schema-1-support.md)

## Out of scope

- Removing historical RFCs, ARPs, specifications, issues, or changelog entries.
- Centralizing skill instructions in a way that breaks selective installation or harness-independent discovery.
- Changing workflow behavior, configuration schema 2, release-bundle contents, or consumer ownership.

## Comments

## Resolution

Resolved on 2026-08-24. Operational lifecycle docs now use release-neutral wording and placeholders, while the smoke test derives `v0.4.0` from release metadata and passed through `skills@latest` plus Pi. Structural verification validates generic operational README links and data-driven current-version changelog readiness instead of accumulating release-specific phrases. Shared consumer fixtures centralize schema-2 configuration, guidance, skill copying, and inventory; v0.3 contract assertions are table-driven with the same required strings and location guards. Generated artifacts and caches are ignored, intentional distribution copies and history remain intact, and all 50 grouped tests plus repository checks pass.
