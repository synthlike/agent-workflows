---
id: ARP-0006
title: Add product-problem framing to v0.3
status: accepted
date: 2026-08-24
supersedes: []
superseded_by:
related_rfcs:
  - ../rfcs/RFC-0005-add-product-problem-framing-to-v0.3.md
---

# Add product-problem framing to v0.3

## Context

The initial v0.3 scope added technical foundations and post-implementation feedback, but left no workflow for challenging a founder's startup premise before product specification. Existing clarification, questionnaire, research, and initiative workflows do not own the complete problem-hypothesis and customer-evidence boundary.

## Decision

v0.3 adds `frame-product-problem` as its seventh new workflow. It interviews the founder one question at a time, separates problem from proposed solution, maps actors and alternatives, exposes risky assumptions and counter-hypotheses, and creates a project-owned supporting brief plus customer-validation plan.

The workflow may reassess assumptions as `Unexamined`, `Supported`, `Weakened`, `Contradicted`, or `Inconclusive` from cited evidence. It may recommend continue, narrow, reframe, pivot, or stop, but only the founder makes the product decision and no validation claim is allowed without customer or behavioral evidence.

This decision refines [ARP-0005](ARP-0005-focus-v0.3-on-project-feedback-workflows.md) from six to seven workflows without changing its schema-2, manual-update, or transactional-maintenance boundary.

## Rationale

Problem framing and technical baselining are complementary project-start operations. Adding the workflow before the v0.3 tag prevents solution-first founder input from flowing directly into specifications or architecture and gives existing research, questionnaire, prototype, and planning workflows a coherent product-discovery entrypoint.

## Consequences

- The v0.3 specification, inventory, documentation, tests, smoke scenario, release asset, and skill count must be amended.
- The problem-framing brief is supporting evidence at a project-approved location, not a new authority type.
- Founder beliefs remain hypotheses until supported by evidence.
- Full business-model, pricing, go-to-market, and technical-feasibility analysis remain separate work.
- v0.3 release preparation remains blocked until the seventh skill is implemented and revalidated.
