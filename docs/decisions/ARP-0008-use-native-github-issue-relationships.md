---
id: ARP-0008
title: Use native GitHub issue relationships
status: accepted
date: 2026-08-25
supersedes: []
superseded_by:
related_rfcs: []
---

# Use native GitHub issue relationships

## Context

The existing GitHub adapter documents basic `gh` commands but leaves initiative hierarchy, blockers, frontier calculation, label setup, pagination, and closure semantics to agent interpretation. Task-list and body-text fallbacks cannot provide reliable relationship queries. GitHub Issues should own bounded work and planning history while durable project authority remains in repository documents.

## Decision

Provide an executable GitHub Cloud helper that implements the issue-backend contract. Configuration records the intended authenticated GitHub login, and every helper operation verifies that account is authenticated and active before repository access; configuration never infers identity from the active account or switches global authentication silently. Initiative maps are parent issues with native sub-issues, blockers use native dependencies, assignees represent claims, and GitHub close reasons distinguish completed from cancelled work. Managed issues have exactly one of seven `workflow:*` semantic-kind labels. Label provisioning requires a reviewed plan. RFCs, ARPs, specifications, domain models, and technical baselines remain repository documents.

## Rationale

Native relationships and deterministic pagination make initiative traversal and frontier selection machine-readable. A small executable helper avoids duplicating fragile REST recipes in every workflow while retaining `gh` authentication and repository discovery. Keeping durable authority in Git preserves reviewable history and prevents the issue backend from becoming a second specification store.

## Consequences

- GitHub Cloud, an explicitly selected authenticated `gh` login, enabled Issues, and sufficient repository permission become backend prerequisites.
- Users with multiple authenticated accounts may need to switch the active account themselves before configuration can continue.
- Repositories must provision the managed labels before creating managed issues.
- The helper must resolve issue numbers to numeric database IDs for relationship operations.
- Claim conflict detection cannot eliminate simultaneous-assignment races because GitHub exposes no atomic claim operation.
- Bear or another artifact store remains a separate future backend concern.

## Evidence

- [GitHub native issue relationship research](../research/2026-08-25-github-native-issue-relationships.md)
- [Complete GitHub issue backend](../../.project/issues/ISSUE-0033-complete-github-issue-backend.md)
