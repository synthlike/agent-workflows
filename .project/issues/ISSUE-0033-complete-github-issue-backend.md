---
id: ISSUE-0033
title: Complete GitHub issue backend
kind: task
status: resolved
created: 2026-08-25
assignee: pi
parent:
blocked_by: []
labels: []
---

# Complete GitHub issue backend

## Question or work

Implement a deterministic GitHub Issues backend helper covering the semantic issue contract. Require native sub-issues and dependencies, model initiatives as parent map issues, bootstrap the approved `workflow:*` kind labels through a reviewed plan, and support paginated stable frontier calculation. Keep authoritative RFCs, ARPs, specifications, domain models, and technical baselines in repository documents.

## Comments

## Resolution

Added an executable GitHub Cloud backend helper with explicit multi-account login selection and identity checks, covering create, read, list, update, comment, claim, resolve, cancel, native parent and blocker operations, and deterministic frontier calculation. Added stale-safe reviewed provisioning for the seven `workflow:*` kind labels, matching generated guidance and helper verification, configuration preflight requirements, update guidance, primary-source research, and ARP-0008. Authoritative RFCs, ARPs, specifications, domain models, and technical baselines remain repository documents. `scripts/verify.sh` passes with 45 tests.
