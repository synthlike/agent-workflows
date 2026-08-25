---
id: ISSUE-0055
title: "Apply approved consumer configuration plans transactionally"
kind: "implementation"
status: resolved
created: 2026-08-25
assignee: "pi"
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

Added source-checkout-free `lifecycle.py apply-consumer`, requiring an exact canonical plan file and separately supplied reviewed `sha256` digest. Apply strictly validates plan and operation shape, digest, bound consumer root, release identity and manifest hash, complete integrity-checked installed inventory, invocation policy and dependency closure, backend capabilities and destinations, canonical re-rendered target set, every prior target state, every copied source path/hash, destination hashes and containment, and managed/lazy directory intent before consumer mutation. It stages every output on the destination filesystem, backs up changed existing files with metadata, rechecks the complete state immediately before mutation, creates only planned managed parents, atomically replaces only changed planned files, runs `verify-consumer` with plan-bound skill paths, and confirms record destinations remain absent. Caught write or verification failures restore prior targets and remove newly created planned directories when safe, with explicit complete/incomplete rollback reporting. Replanning applied identical intent produces unchanged targets and a no-op apply. Skills, record destinations, backend state, and provider configuration are never mutation targets; GitHub labels remain separate. Added success, canonical/digest tamper, stale state, malicious recomputed plan, exact-root-guidance preservation, skill immutability, source-checkout-free CLI, verification/write rollback, stage cleanup, and no-op regressions. Updated authoritative and user guidance plus the changelog. `scripts/verify.sh` passes with 156 tests.
