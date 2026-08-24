---
id: ISSUE-0031
title: Remove release-bundle installation
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent:
blocked_by: []
labels: [v0.5, lifecycle, installation]
---

# Remove release-bundle installation

## What to build

Remove the custom archive distribution and missing-skill application mechanism. Require complete skill installation through an external installer or intact manual copy, then use the embedded manifest for inventory, closure, and installed verification.

## Acceptance criteria

- [x] `configure-project` requires all distributed skills and reports incomplete installation without trying to add files.
- [x] Bundle build, validation, download, staging, planning, and apply commands and modules are removed.
- [x] Bundle and fresh-apply tests are removed; manifest, closure, consumer verification, complete-install smoke, and documentation checks remain.
- [x] Active onboarding, distribution, adoption, update, dependency, and skill guidance contain no release-bundle mechanism.
- [x] The accepted decision and its consequences are recorded without rewriting historical RFCs, ARPs, specifications, changelog entries, or resolved issues.
- [x] Generated manifest is current and repository verification passes.

## Blocked by

None.

## Out of scope

- An in-repository installer.
- Automated updates or replacement of consumer-owned skill directories.
- Rewriting historical artifacts.

## Comments

## Resolution

Resolved on 2026-08-24. ARP-0007 establishes complete external installation as the sole supported model. `configure-project` and its lifecycle command now inspect, calculate closure, and verify but never create or replace skill directories. The custom archive, download, validation, staging, fresh-plan, and apply implementation and tests were removed. Active documentation now describes only complete installation and the deterministic distribution manifest; historical release records remain intact with decision cross-links. The real `skills@latest` and Pi smoke test installed and discovered all 20 skills, selected one workflow in schema 2, verified without a source checkout, and preserved lazy directories. All 32 remaining tests and repository checks pass.
