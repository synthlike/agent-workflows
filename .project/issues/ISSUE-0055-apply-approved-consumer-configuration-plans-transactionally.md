---
id: ISSUE-0055
title: "Apply approved consumer configuration plans transactionally"
kind: "implementation"
status: open
created: 2026-08-25
assignee: 
parent: "ISSUE-0050-streamline-deterministic-consumer-configuration.md"
blocked_by:
  - "ISSUE-0054-generate-deterministic-consumer-configuration-plans.md"
labels: ["lifecycle","configuration"]
---
# Apply approved consumer configuration plans transactionally

## Parent

Streamline deterministic consumer configuration

## What to build

Add `apply-consumer` so an exact approved plan mechanically writes only planned consumer configuration, guidance, and backend assets, rejects stale state, and restores prior files on caught failure.

## Acceptance criteria

- [ ] Apply requires the plan file and exact expected `sha256` digest, validates canonical plan bytes, release identity, consumer root, installed inventory, and operation schema.
- [ ] Before any write it rechecks every target's expected hash or absence, every bundled source hash, all destination containment, and the complete planned target set.
- [ ] It stages every output on the destination filesystem, then writes only planned files and creates only planned guidance/configuration parent directories.
- [ ] It never creates record destination directories and never installs, replaces, removes, or modifies skill directories.
- [ ] Existing root guidance outside the managed section is preserved exactly.
- [ ] Caught write or verification failure restores every prior target and removes newly created planned files/directories when safe, then reports recovery outcome.
- [ ] Successful apply runs `verify-consumer` using the plan-bound discovered inventory and reports resulting files and intentionally absent directories.
- [ ] A stale target or altered plan fails before writes; replanning identical already-applied intent produces a no-op plan and apply changes nothing.
- [ ] GitHub label provisioning remains a separate external approval and operation.

## Blocked by

Deterministic consumer plan generation.

## Out of scope

Skill updates, backend records, label application, schema migration, and interruption recovery after an uncatchable process or machine failure.

## Comments


## Resolution
