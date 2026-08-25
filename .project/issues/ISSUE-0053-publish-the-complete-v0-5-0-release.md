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
  - "ISSUE-0066-add-migrate-records-and-full-migration-conformance.md"
labels: ["lifecycle","configuration"]
---
# Publish the complete v0.5.0 release

## Parent

Streamline deterministic consumer configuration

## What to build

Publish one immutable release containing schema-3 routing, Bear non-issue support, corrected discovery semantics, conditional backend inspection, canonical templates, deterministic consumer plan/apply, strict cross-backend record migration, and complete current documentation.

## Acceptance criteria

- [ ] Bear documentation and optional smoke behavior from ISSUE-0049 are complete.
- [ ] Discovery, conditional inspection, canonical templates, deterministic `plan-consumer`/`apply-consumer`, and the complete `migrate-records` distribution are integrated into release metadata and the generated manifest.
- [ ] Strict one-route migration passes the full capability-compatible local Markdown/GitHub/Bear matrix with active/history fidelity, resumable journals, separately approved copy/cutover/retirement, configuration plan/apply reuse, roll-forward recovery, and source retention.
- [ ] Changelog and active documentation accurately describe all v0.5.0 behavior, approval boundaries, and limitations.
- [ ] The complete repository suite, source-checkout-free configuration and migration scenarios, fresh local smoke, and approved read-only provider checks pass.
- [ ] Release metadata identifies exactly `v0.5.0` and all committed release assets are canonical.
- [ ] After separate final publication approval, the release commit is tagged, pushed, and published as an immutable GitHub release without patching any consumer installation.

## Blocked by

Bear documentation/smoke completion, corrected discovery semantics, canonical templates, deterministic configuration, and complete strict migration conformance.

## Out of scope

Unapproved provider mutation, skill installation or replacement, semantic reclassification, free-form link rewriting, source deletion, Things, and schema migration.

## Comments


## Resolution
