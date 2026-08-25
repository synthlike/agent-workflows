---
id: ISSUE-0032
title: Configure supporting artifact retention
kind: task
status: resolved
created: 2026-08-25
assignee: pi
parent:
blocked_by: []
labels: []
---

# Configure supporting artifact retention

## Question or work

Add repository-retention capabilities for research, questionnaires, technical baselines, prototypes, and handoffs. Configure fresh projects according to their nature and collaboration model, with reviewed defaults and repository-contained paths. Update affected workflows, examples, guidance, validation coverage, and release integrity metadata.

## Comments

## Resolution

Added configurable repository retention and paths for research, questionnaires, technical baselines, prototypes, and handoffs. Fresh defaults retain the first three and keep prototypes and handoffs external or temporary. `configure-project` now asks about project nature and collaboration, uses repository evidence, and confirms each recommendation individually. Updated affected workflows, examples, project guidance, tests, and the release manifest. `scripts/verify.sh` passes.
