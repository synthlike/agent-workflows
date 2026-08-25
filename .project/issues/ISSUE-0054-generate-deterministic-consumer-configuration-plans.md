---
id: ISSUE-0054
title: "Generate deterministic consumer configuration plans"
kind: "implementation"
status: resolved
created: 2026-08-25
assignee: "pi"
parent: "ISSUE-0050-streamline-deterministic-consumer-configuration.md"
blocked_by:
  - "ISSUE-0051-correct-discovery-semantics-and-inspect-backends-conditionally.md"
  - "ISSUE-0052-bundle-canonical-consumer-guidance-templates.md"
labels: ["lifecycle","configuration"]
---
# Generate deterministic consumer configuration plans

## Parent

Streamline deterministic consumer configuration

## What to build

Add a source-checkout-free `plan-consumer` lifecycle command that converts normalized approved intent and an integrity-checked installation into one immutable review artifact without changing the consumer.

## Acceptance criteria

- [ ] A strict versioned JSON answer schema supports explicit selections or `all`, project summary/documentation style, named backends, one local-default profile, and explicit per-route overrides.
- [ ] The plan contains exact bytes for every generated text file, source and destination hashes for copied backend assets, expected prior hash or absence for every target, directories to create, directories deliberately left absent, normalized selected workflows, complete installed inventory, and immutable distribution identity.
- [ ] Plan identity is `sha256` over canonical JSON excluding only its digest field; identical consumer state and answers produce byte-identical plans.
- [ ] Planning reads canonical bundled templates and adapter assets rather than hand-authoring YAML or Markdown.
- [ ] Planning rejects malformed, incomplete, unsupported, escaping, colliding, or stale inputs without consumer writes.
- [ ] Existing root guidance is incorporated into exact planned bytes while preserving unrelated content.
- [ ] Local-only planning invokes neither `gh` nor `bearcli`; provider preflight remains conditional workflow evidence outside local file generation.
- [ ] Planning never installs or changes skill directories, backend state, record destinations, configuration, or guidance.

## Blocked by

Corrected discovery semantics and canonical templates.

## Out of scope

Plan application, schema migration, provider provisioning, and skill installation or replacement.

## Comments
## Resolution

Added source-checkout-free `lifecycle.py plan-consumer` and a strict version-1 JSON answer schema. Answers support `all` or explicit workflow selection, project summary and documentation style, named local/GitHub/Bear instances, the `local-default` profile, partial explicit route overrides, a selected root-guidance file, and expected prior hashes or absence for every managed target. Planning integrity-checks the complete installation, validates routes through the same adapter capability and destination rules as consumer verification, renders only through canonical bundled templates/assets, incorporates existing root guidance, and rejects malformed, incomplete, unsupported, escaping, colliding, ambiguous, or stale state without writes. Canonical plans contain immutable distribution identity and manifest hash; normalized selections, closure, invocation policy, and complete installed paths; exact UTF-8 generated content; copied-asset source paths and source/destination hashes; expected prior state for every target; managed directories to create; lazy local record directories deliberately left absent; and a `sha256` digest over canonical JSON excluding only the digest. Added byte-determinism, digest, local and mixed route, exact asset, stale/error, preservation, source-checkout-free CLI, no-write, and failing-`gh`/`bearcli` sentinel regressions. Updated the authoritative routing specification, lifecycle/configuration guidance, skill guidance, templates, and changelog. `scripts/verify.sh` passes with 149 tests.
