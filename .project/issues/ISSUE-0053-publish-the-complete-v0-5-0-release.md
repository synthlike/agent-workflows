---
id: ISSUE-0053
title: "Publish the complete v0.5.0 release"
kind: "implementation"
status: resolved
created: 2026-08-25
assignee: "pi"
parent: "ISSUE-0050-streamline-deterministic-consumer-configuration.md"
blocked_by:
  - "ISSUE-0049-document-and-smoke-test-bear-routing.md"
  - "ISSUE-0051-correct-discovery-semantics-and-inspect-backends-conditionally.md"
  - "ISSUE-0052-bundle-canonical-consumer-guidance-templates.md"
labels: ["lifecycle","configuration"]
---
# Publish the complete v0.5.0 release

## Parent

Streamline deterministic consumer configuration

## What to build

Publish one immutable release containing schema-3 routing, Bear non-issue support, corrected discovery semantics, conditional backend inspection, canonical templates, deterministic consumer plan/apply, and complete current documentation.

## Acceptance criteria

- [x] Bear documentation and optional smoke behavior from ISSUE-0049 are complete.
- [x] Discovery, conditional inspection, canonical templates, and deterministic `plan-consumer`/`apply-consumer` are integrated into release metadata and the generated manifest.
- [x] Changelog and active documentation accurately describe all v0.5.0 behavior, approval boundaries, non-migrating route behavior, and limitations.
- [x] The complete repository suite, source-checkout-free configuration scenarios, fresh local smoke, and approved read-only provider checks pass.
- [x] Release metadata identifies exactly `v0.5.0` and all committed release assets are canonical.
- [x] After separate final publication approval, the release commit is tagged, pushed, and published as an immutable GitHub release without patching any consumer installation.

## Blocked by

Bear documentation/smoke completion, corrected discovery semantics, canonical templates, and deterministic configuration.

## Out of scope

Unapproved provider mutation, skill installation or replacement, record migration, semantic reclassification, free-form link rewriting, source deletion, Things, and schema migration.

## Comments

### 2026-08-27T19:09:29Z — pi

Release verification passed: `scripts/verify.sh` ran 164 tests; the source-checkout-free `skills@latest` and Pi fresh-install smoke passed; GitHub preflight confirmed `synthlike/agent-workflows` as `synthlike` with ADMIN permission and complete contracts; Bear CLI 2.9.3 scoped preflight passed read-only for `agent-workflows/preflight`. No provider mutation was performed.
## Resolution

Published immutable `v0.5.0` from commit `6e1a2948263da68986181ba018d14cfb23829c6e`. The annotated tag and `main` were pushed, and the non-draft, non-prerelease GitHub release was verified at the provider-returned release URL. The release contains schema-3 routing, Local Markdown/GitHub/Bear backend support, corrected discovery semantics, canonical templates, and deterministic transactional consumer plan/apply. Record migration remains outside the core scope under ARP-0011.
