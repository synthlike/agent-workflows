---
id: ISSUE-0025
title: Implement frame-product-problem
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent: ../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md
blocked_by:
  - ISSUE-0024-add-product-problem-framing-to-v0.3-scope.md
labels: [v0.3, skill]
---

# Implement frame-product-problem

## Parent

[v0.3 product-foundation and feedback workflows](../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md)

## What to build

Add a workflow that interviews a founder, challenges a solution-first startup premise, creates a project-owned problem-framing brief and customer-validation plan, and later reassesses assumptions from cited evidence.

## Acceptance criteria

- [x] The skill interviews one question at a time and separates solution, problem, actors, context, trigger, alternatives, workarounds, and desired outcome.
- [x] Founder beliefs, observations, external evidence, interpretations, and unknowns remain distinct.
- [x] The skill challenges frequency, consequence, audience boundaries, counter-hypotheses, and willingness to change or pay without expanding into full business-model analysis.
- [x] A project-approved problem-framing brief records risky assumptions, evidence thresholds, unresolved questions, and authority links without claiming validation.
- [x] The validation plan and non-leading questionnaire prefer concrete past behavior and respect consent, privacy, and confidential information.
- [x] Reassessment uses the five accepted evidence states and may recommend continue, narrow, reframe, pivot, or stop while leaving the decision to the founder.
- [x] Founder, customer, contradictory-evidence, existing-guidance, denied-write, and unsupported-validation scenarios verify the contract.
- [x] README, selection guidance, artifact guidance, changelog, schema-2 inventory, dependency table, tests, and manifest include the twentieth skill.
- [x] All repository verification passes.

## Blocked by

- [Add product-problem framing to v0.3 scope](ISSUE-0024-add-product-problem-framing-to-v0.3-scope.md)

## Out of scope

- Performing customer interviews without a human participant and consent.
- Declaring the startup idea validated from founder discussion.
- Full pricing, market sizing, unit economics, go-to-market, fundraising, technical feasibility, specification, or implementation planning.

## Comments

## Resolution

Resolved on 2026-08-24. `frame-product-problem` now interviews a founder one question at a time, separates solution and problem claims, distinguishes actors and evidence classes, challenges counter-hypotheses and willingness to change, and creates an approved supporting brief and non-leading validation plan. It reassesses assumptions through five evidence states without claiming validation or taking the founder's decision. README, workflow and artifact guidance, schema-2 inventory, dependency closure, manifest, and five new contract scenarios include the twentieth skill; all 80 tests pass.
