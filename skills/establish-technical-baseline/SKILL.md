---
name: establish-technical-baseline
description: Establish a minimal production-compatible engineering foundation for an already selected technical stack without inventing product-dependent architecture.
license: MIT
---

# Establish Technical Baseline

Turn fixed technology choices into reviewed engineering guardrails. Do not select the stack or infer product architecture from it.

## Establish the boundary

Read project guidance, existing engineering or architecture documentation, accepted ARPs, open RFCs, specifications, dependency manifests, build and test entrypoints, deployment configuration, and repository status.

Confirm only information the repository does not establish:

- fixed technologies, supported versions, and deployment constraints;
- intended maturity, defaulting to a minimal but production-compatible foundation;
- known quality, security, regulatory, and operational constraints; and
- the product questions that are deliberately still unknown.

A minimal production-compatible foundation addresses guardrails expensive to retrofit. It does not predict product behavior, domain boundaries, tenancy, consistency, scale, or data access patterns without evidence.

## Verify the stack

Prefer official documentation, specifications, support policies, and first-party platform guidance. Invoke `research-question` for a focused external uncertainty that materially affects the baseline.

Classify every material statement as one of:

- **Verified fact:** supported by repository or cited primary evidence;
- **Approved convention:** a reversible project practice confirmed by the user;
- **Recommendation:** context-dependent advice awaiting approval;
- **Accepted decision:** linked to its ARP;
- **Open decision:** linked to an RFC or proposed as an RFC question; or
- **Deferred product question:** unsafe to answer before product or domain evidence exists.

Never present generic agent knowledge as a verified compatibility fact. Surface unsupported versions, contradictory constraints, missing operational prerequisites, and choices that cannot remain safely deferred.

## Assess applicable foundations

Consider only areas relevant to the selected stack:

- repository structure and dependency boundaries;
- runtime and toolchain version policy;
- configuration and secret handling;
- local development and reproducible setup;
- test layers and stable verification commands;
- build, deployment, and environment promotion;
- logging, metrics, tracing, and operational ownership;
- security and supply-chain controls; and
- data lifecycle, backup, recovery, and migration conventions.

Routine reversible conventions may remain in the baseline. Use `develop-rfc` for a consequential unresolved choice. After the decision owner accepts a consequential outcome, use `record-arp`; link the ARP instead of copying its decision into the baseline. Agreed product behavior belongs in a specification, executable work in an issue, domain terminology in domain documentation, and current behavior in code and tests.

## Choose a location

Prefer an existing project-approved engineering or architecture documentation location. If none exists, propose a repository-contained location and ask the user to approve it. Do not assume a fixed directory or create optional directories before their first approved document.

Use [the baseline template](references/technical-baseline-template.md). The baseline is a supporting index and project guidance, not a new authority for decisions or behavior.

## Confirm

Show a complete dry run containing:

1. fixed inputs and maturity target;
2. verified facts with sources;
3. contradictions and unsafe-to-defer gaps;
4. proposed conventions and recommendations;
5. open RFC questions and deferred product questions;
6. the exact target path and document outline; and
7. every file that would be created or changed.

Wait for explicit approval. Preserve existing documentation and conventions; update rather than replace related guidance.

## Write and report

Write only the approved baseline and approved links or guidance changes. Do not create RFCs, ARPs, specifications, or issues without their separate workflow approvals.

Report the baseline path, evidence consulted, approved conventions, linked decisions, open questions, deferred product questions, verification performed, and every changed file. If evidence is insufficient or constraints conflict, stop with the supported findings and the smallest question or investigation needed next; do not claim that a baseline is established.
