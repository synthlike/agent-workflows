---
id: ISSUE-0030
title: Recommend complete skill installation
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent:
blocked_by: []
labels: [documentation, installation]
---

# Recommend complete skill installation

## What to build

Make installing all distributed skills through an Agent Skills-compatible installer the default onboarding path. Keep selective bundle-backed dependency completion as an advanced reproducible option.

## Acceptance criteria

- [x] README quick start installs all skills while project configuration still records explicit workflow intent.
- [x] Fresh-project and existing-project guidance recommend complete installation without weakening non-destructive ownership rules.
- [x] Selective installation, deterministic bundles, dependency closure, and the maintainer smoke test remain documented and supported.
- [x] Documentation explains that a complete install avoids requiring a release bundle during normal fresh setup.
- [x] Repository verification passes.

## Blocked by

None.

## Out of scope

- Removing bundle or closure support.
- Changing skill behavior or the schema-2 configuration format.

## Comments

## Resolution

Resolved on 2026-08-24. The README and project-adoption guides now recommend copying all 20 skills with `--skill '*' --copy`, then recording only the user's explicit workflow intent as selected configuration. Normal complete setup no longer needs a release bundle. Selective bundle-backed closure remains documented as an advanced path, retains all non-destructive checks, and remains exercised by the real installer and Pi smoke test. All 50 grouped tests and repository checks pass.
