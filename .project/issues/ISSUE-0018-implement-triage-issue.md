---
id: ISSUE-0018
title: Implement triage-issue
kind: task
status: open
created: 2026-08-24
assignee:
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

- [ ] The skill reads backend instructions, searches existing issues and authority, and checks duplicates and prior dispositions.
- [ ] It classifies reports without inventing severity, urgency, business impact, or implementation detail.
- [ ] Missing evidence and decision needs route to failure investigation, research, clarification, or RFC development as appropriate.
- [ ] An issue proposal contains one bounded outcome, observable acceptance criteria, relevant links, and genuine blockers.
- [ ] Classification, duplicate analysis, evidence, missing facts, scope, criteria, and routing receive approval before issue creation or material rewrite.
- [ ] Duplicate, uncertain-defect, design-ambiguity, and actionable-change scenarios verify routing and backend safety.
- [ ] v0.3 release metadata, schema-2 source inventory, dependency documentation, generated manifest, and verification include the skill.
- [ ] All repository verification passes.

## Blocked by

- [Implement investigate-failure](ISSUE-0016-implement-investigate-failure.md)

## Out of scope

- Implementing the triaged work.
- Silently resolving ambiguity or accepting a technical decision.
- Creating an issue for every report regardless of disposition.
