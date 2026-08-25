---
id: ISSUE-0054
title: "Generate deterministic consumer configuration plans"
kind: "implementation"
status: open
created: 2026-08-25
assignee: 
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
