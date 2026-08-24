---
id: ARP-0007
title: Install the complete skill distribution
status: accepted
date: 2026-08-24
supersedes: []
superseded_by:
related_rfcs: []
---

# Install the complete skill distribution

## Context

The decision owner confirmed this outcome in [ISSUE-0031](../../.project/issues/ISSUE-0031-remove-release-bundle-installation.md).

The fresh-project lifecycle originally accepted a small initial selection and used a custom deterministic archive to add its transitive dependencies. The distribution now contains only 20 small skills, while the archive adds release publication, download, validation, staging, transaction, documentation, and test surfaces. Normal users already rely on an Agent Skills-compatible installer, and requiring a second distribution format makes setup harder to explain and complete.

## Decision

A supported installation contains the complete Agent Workflows skill distribution. Users install it through an external installer or an intact manual copy at repository-contained paths discovered by their harness. `configure-project` records explicitly selected workflow intent separately from the complete installed inventory.

The embedded distribution manifest remains authoritative for release identity, skill inventory, dependencies, and file hashes. The installed lifecycle command retains manifest generation and checking, closure calculation, inspection, and schema-2 consumer verification. Configuration stops and reports the missing skills when the complete distribution is absent; it does not obtain or write skill files.

The custom release archive and its build, validation, download, staging, planning, and apply commands are removed. This decision revises the archive and missing-dependency portions of [ARP-0002](ARP-0002-use-configure-project-as-the-lifecycle-bootstrap.md) and [ARP-0004](ARP-0004-ship-v0.2-for-fresh-project-adoption.md); their manifest, schema-2 inventory, installed verification, and consumer-ownership decisions remain accepted.

## Rationale

Installing all 20 skills has negligible storage cost and gives users one installation model. External installers already solve copying and harness placement. Keeping the manifest and source-checkout-free verifier preserves deterministic integrity checks without maintaining a second installer inside `configure-project`.

## Consequences

- Users must install all distributed skills before configuration can finish.
- Explicitly selected workflows remain distinct from installed inventory.
- `configure-project` never creates, replaces, or removes a skill directory.
- Missing or modified skills are reported for the user to correct through their installer or reviewed manual copy.
- Release publication no longer requires a custom archive asset.
- Selective installations and offline dependency completion are unsupported.
- Historical records continue to describe the behavior of earlier releases.
