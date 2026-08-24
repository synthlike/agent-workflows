---
id: ISSUE-0029
title: Make the README approachable
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent:
blocked_by: []
labels: [documentation]
---

# Make the README approachable

## What to build

Restructure the README around user outcomes, common scenarios, a short setup path, and a copyable first prompt. Move lifecycle internals and design history below the onboarding path without weakening safety or ownership guidance.

## Acceptance criteria

- [x] The opening explains who the workflows help and what users can accomplish.
- [x] A scenario table maps common goals to starting workflows.
- [x] Quick start shows a minimal install, an agent prompt, and the approval boundary.
- [x] Founder discovery has a concrete first-use route and one-question-at-a-time prompt.
- [x] Current guarantees, ownership, limitations, operational references, and design history remain discoverable.
- [x] The repository moves to the next unreleased distribution identity before changing bundled source documentation.
- [x] Repository verification passes.

## Blocked by

None.

## Out of scope

- Workflow behavior changes.
- Installer or lifecycle changes.

## Comments

## Resolution

Resolved on 2026-08-24. The README now leads with user outcomes, maps common scenarios to starting workflows, gives a minimal installation and approval-aware setup prompt, and walks through the founder-discovery route. Ownership, guarantees, limitations, operations, and design history remain available below the onboarding path. The unreleased repository identity advanced to v0.5.0, its generated manifest was refreshed, and all 50 grouped tests plus repository checks pass.
