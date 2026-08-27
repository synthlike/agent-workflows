---
id: ISSUE-0053
title: "Publish the complete v0.5.0 release"
kind: "implementation"
status: open
created: 2026-08-25
assignee: 
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

- [ ] Bear documentation and optional smoke behavior from ISSUE-0049 are complete.
- [ ] Discovery, conditional inspection, canonical templates, and deterministic `plan-consumer`/`apply-consumer` are integrated into release metadata and the generated manifest.
- [ ] Changelog and active documentation accurately describe all v0.5.0 behavior, approval boundaries, non-migrating route behavior, and limitations.
- [ ] The complete repository suite, source-checkout-free configuration and migration scenarios, fresh local smoke, and approved read-only provider checks pass.
- [ ] Release metadata identifies exactly `v0.5.0` and all committed release assets are canonical.
- [ ] After separate final publication approval, the release commit is tagged, pushed, and published as an immutable GitHub release without patching any consumer installation.

## Blocked by

Bear documentation/smoke completion, corrected discovery semantics, canonical templates, and deterministic configuration.

## Out of scope

Unapproved provider mutation, skill installation or replacement, record migration, semantic reclassification, free-form link rewriting, source deletion, Things, and schema migration.

## Comments


## Resolution
