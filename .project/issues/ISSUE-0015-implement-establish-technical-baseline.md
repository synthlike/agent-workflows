---
id: ISSUE-0015
title: Implement establish-technical-baseline
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent: ../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md
blocked_by: []
labels: [v0.3, skill]
---

# Implement establish-technical-baseline

## Parent

[v0.3 project-foundation and feedback workflows](../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md)

## What to build

Add a workflow that turns an already selected technical stack into a minimal, production-compatible engineering foundation without inventing product-dependent architecture.

## Acceptance criteria

- [x] The skill establishes fixed technologies, maturity target, repository context, compatibility facts, baseline areas, and unsafe-to-defer gaps from project evidence and high-trust primary sources.
- [x] Recommendations distinguish facts, approved conventions, open decisions, accepted decisions, and deferred product questions.
- [x] The skill proposes a project-owned location and complete dry run before writing a durable baseline index and never hardcodes a consumer path.
- [x] A reusable baseline reference keeps authority in RFCs, ARPs, specifications, domain docs, issues, code, and tests.
- [x] Empty-project and existing-guidance scenarios verify location approval, convention preservation, and product-architecture deferral.
- [x] v0.3 release metadata, schema-2 source inventory, dependency documentation, generated manifest, and verification include the skill.
- [x] All repository verification passes.

## Blocked by

None.

## Out of scope

- Selecting a project's principal technologies.
- Deciding product behavior, domain architecture, tenancy, consistency, or scale without product evidence.
- Introducing a fixed technical-baseline directory or new configuration schema.

## Comments

## Resolution

Resolved on 2026-08-24. `establish-technical-baseline` now establishes a minimal production-compatible foundation from fixed stack constraints, repository evidence, and primary sources; classifies facts, conventions, recommendations, decisions, and deferred product questions; requires location and write approval; and produces a supporting index from a reusable template without hardcoded consumer paths. v0.3 metadata, the schema-2 source inventory, dependency table, and generated manifest include the skill. Four contract scenarios and all 60 repository tests pass.
