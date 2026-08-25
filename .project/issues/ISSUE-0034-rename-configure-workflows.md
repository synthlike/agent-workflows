---
id: ISSUE-0034
title: Rename configure-workflows to configure-workflows
kind: task
status: resolved
created: 2026-08-25
assignee: pi
parent:
blocked_by: []
labels: []
---

# Rename configure-workflows to configure-workflows

## Question or work

Rename the mandatory workflow bootstrap skill from `configure-workflows` to `configure-workflows` across its directory, frontmatter, lifecycle contract, release metadata and manifest, consumer configuration, documentation, examples, scripts, tests, and historical repository references. No compatibility alias or migration is required because there are no external consumers.

## Comments

## Resolution

Renamed the mandatory bootstrap skill and directory to `configure-workflows`. Updated lifecycle closure and integrity handling, release metadata and manifest, consumer configuration, generated paths, workflow references, documentation, examples, scripts, tests, and internal historical references. Renamed ARP-0002 for consistent links. No alias or migration path was retained. `scripts/verify.sh` passes with 47 tests.
