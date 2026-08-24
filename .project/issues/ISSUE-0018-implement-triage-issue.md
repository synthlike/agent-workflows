---
id: ISSUE-0018
title: Implement triage-issue
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent: ../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md
blocked_by:
  - ISSUE-0016-implement-investigate-failure.md
labels: [v0.3, skill]
---

# Implement triage-issue

## Parent

[v0.3 project-foundation and feedback workflows](../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md)

## What to build

Add a workflow that evaluates an incoming report, identifies its correct disposition, and proposes actionable issue scope or another workflow before any backend write.

## Acceptance criteria

- [x] The skill reads backend instructions, searches existing issues and authority, and checks duplicates and prior dispositions.
- [x] It classifies reports without inventing severity, urgency, business impact, or implementation detail.
- [x] Missing evidence and decision needs route to failure investigation, research, clarification, or RFC development as appropriate.
- [x] An issue proposal contains one bounded outcome, observable acceptance criteria, relevant links, and genuine blockers.
- [x] Classification, duplicate analysis, evidence, missing facts, scope, criteria, and routing receive approval before issue creation or material rewrite.
- [x] Duplicate, uncertain-defect, design-ambiguity, and actionable-change scenarios verify routing and backend safety.
- [x] v0.3 release metadata, schema-2 source inventory, dependency documentation, generated manifest, and verification include the skill.
- [x] All repository verification passes.

## Blocked by

- [Implement investigate-failure](ISSUE-0016-implement-investigate-failure.md)

## Out of scope

- Implementing the triaged work.
- Silently resolving ambiguity or accepting a technical decision.
- Creating an issue for every report regardless of disposition.

## Comments

## Resolution

Resolved on 2026-08-24. `triage-issue` now loads configured backend and authority, checks functional duplicates and prior disposition, separates reported impact from verified evidence and stakeholder priority, routes missing evidence or decisions, and drafts one approved disposition before any backend write. Its proposal template supports duplicate, question, evidence, routed, new-issue, and issue-update outcomes. v0.3 inventory, dependency closure, manifest, and three new contract scenarios are verified; all 69 tests pass.
