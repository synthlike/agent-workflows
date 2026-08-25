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

Publish the first immutable release containing schema-3 routing, Bear non-issue support, corrected discovery semantics, conditional backend inspection, canonical templates, and complete current documentation.

## Acceptance criteria

- [ ] Bear documentation and optional smoke behavior from ISSUE-0049 are complete.
- [ ] Discovery, conditional inspection, and canonical templates are integrated into release metadata and the generated manifest.
- [ ] Changelog and active documentation accurately describe v0.5.0 behavior and limitations.
- [ ] The complete repository suite, source-checkout-free verification, fresh local smoke, and approved read-only provider checks pass.
- [ ] Release metadata identifies exactly `v0.5.0` and all committed release assets are canonical.
- [ ] After separate final publication approval, the release commit is tagged, pushed, and published as an immutable GitHub release without patching any consumer installation.

## Blocked by

Bear documentation/smoke completion, corrected discovery semantics, and canonical templates.

## Out of scope

Deterministic consumer plan/apply, skill-directory updates, and GitHub label mutation.

## Comments


## Resolution
