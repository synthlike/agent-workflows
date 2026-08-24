---
id: ISSUE-0021
title: Integrate and document the v0.3 workflow set
kind: task
status: open
created: 2026-08-24
assignee:
parent: ../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md
blocked_by:
  - ISSUE-0015-implement-establish-technical-baseline.md
  - ISSUE-0016-implement-investigate-failure.md
  - ISSUE-0017-implement-capture-regression.md
  - ISSUE-0018-implement-triage-issue.md
  - ISSUE-0019-implement-review-implementation.md
  - ISSUE-0020-implement-close-initiative.md
labels: [v0.3, integration, documentation]
---

# Integrate and document the v0.3 workflow set

## Parent

[v0.3 project-foundation and feedback workflows](../../docs/specifications/v0.3-project-foundation-and-feedback-workflows.md)

## What to build

Present the six new skills as one coherent project-foundation and feedback lifecycle, with complete routing, dependency, configuration, adoption, customization, and manual-update guidance.

## Acceptance criteria

- [ ] README and workflow documentation explain when and how the six skills connect without duplicating their contracts.
- [ ] Artifact guidance identifies the technical baseline as a supporting project-owned index and preserves existing authority boundaries.
- [ ] Dependency documentation and tests verify exact direct dependencies and closure for every new selectable skill.
- [ ] Contract verification covers every new skill's trigger, inspection, proposal, approval, write, output, stop, and preservation behavior.
- [ ] Configuration examples and the source repository inventory remain schema 2 and contain exact discovered paths.
- [ ] Customization and update guidance preserve project ownership and the reviewed manual update boundary.
- [ ] Changelog and release documentation describe the complete v0.3 scope and provisional update deferral.
- [ ] The generated manifest and deterministic bundle contain the complete 19-skill distribution.
- [ ] All repository verification passes.

## Blocked by

- [Implement establish-technical-baseline](ISSUE-0015-implement-establish-technical-baseline.md)
- [Implement investigate-failure](ISSUE-0016-implement-investigate-failure.md)
- [Implement capture-regression](ISSUE-0017-implement-capture-regression.md)
- [Implement triage-issue](ISSUE-0018-implement-triage-issue.md)
- [Implement review-implementation](ISSUE-0019-implement-review-implementation.md)
- [Implement close-initiative](ISSUE-0020-implement-close-initiative.md)

## Out of scope

- Adding another workflow.
- Transactional updates or configuration schema 3.
- Duplicating detailed skill contracts in overview documentation.
