---
id: RFC-0004
title: Focus v0.3 on project foundations and feedback workflows
status: accepted
authors: [synthlike]
created: 2026-08-24
decision_owner: synthlike
related_arps:
  - ../decisions/ARP-0005-focus-v0.3-on-project-feedback-workflows.md
---

# Focus v0.3 on project foundations and feedback workflows

## Summary

Decide whether v0.3 should implement the reusable update and recovery lifecycle deferred by [ARP-0004](../decisions/ARP-0004-ship-v0.2-for-fresh-project-adoption.md) or add workflows that address gaps before project design and after implementation.

v0.3 will retain schema 2 and reviewed manual updates. It will add six harness- and technology-independent skills: `establish-technical-baseline`, `triage-issue`, `investigate-failure`, `capture-regression`, `review-implementation`, and `close-initiative`. Transactional update automation becomes provisional v0.4 scope unless adoption or update pain justifies earlier reprioritization.

## Motivation

v0.2 established deterministic releases, dependency-complete fresh installation, schema-2 inventory, and installed verification. The toolkit now has strong workflows for clarification, domain modeling, research, decisions, specifications, and planning, but it has two practical gaps:

- a project with an already selected technical stack lacks a workflow for establishing a minimal, production-compatible engineering foundation before product discovery; and
- implementation findings, failures, regressions, conformance review, and initiative outcomes lack a coherent feedback loop.

There is not yet evidence that a transaction engine provides more immediate value than these semantic workflows. A partial updater would add integrity-sensitive behavior without resolving rollback and interruption recovery completely.

## Requirements and constraints

### Requirements

- v0.3 MUST add `establish-technical-baseline` for projects whose principal technologies are already constraints. It MUST use high-trust primary guidance, establish only a minimal production-compatible foundation, separate stack-level guardrails from product-dependent architecture, and create a durable baseline index at a project-approved location.
- The technical baseline MUST distinguish verified facts, approved conventions, recommendations, accepted decisions, unresolved RFC candidates, and deferred product questions. It MUST link ARPs rather than duplicate their authority.
- v0.3 MUST add `triage-issue` to classify an incoming report, inspect duplicates and authoritative context, identify missing evidence, and propose one actionable issue or routing outcome. It MUST obtain approval before creating or materially rewriting an issue.
- v0.3 MUST add `investigate-failure` to reproduce a failure, compare expected and observed behavior, test competing hypotheses, and identify a root cause or bounded uncertainty. It MUST diagnose rather than implement a permanent fix.
- v0.3 MUST add `capture-regression` to encode an accepted defect as the smallest durable automated check at the appropriate test level. It MUST prove that the check fails for the diagnosed reason and MUST NOT change production behavior. A project MAY land the check with its fix when committed failing tests are prohibited.
- v0.3 MUST add `review-implementation` to inspect actual code, configuration, tests, documentation, and relevant repository state against the implementation issue, agreed specification, and accepted ARPs. RFC discussion MAY supply context but MUST NOT override authoritative requirements.
- Implementation review MUST be read-only, cite concrete evidence, and return `Conforms`, `Conforms with follow-up`, or `Does not conform`. It MUST NOT change issue status or create follow-up work without approval.
- v0.3 MUST add `close-initiative` to verify evidence and record an `Achieved`, `Partially achieved`, or `Abandoned` outcome. It MUST identify remaining work and MUST NOT present deferred or cancelled scope as delivered.
- Except for the project-approved technical baseline index, the new workflows MUST use existing authoritative artifacts and supporting-evidence locations rather than introduce canonical report types or fixed directories.
- Every skill MUST remain independent of a specific application, programming language, framework, cloud, database, issue tracker, test framework, documentation generator, agent harness, or skill parent path.
- v0.3 MUST retain configuration schema 2 and the vendored consumer-ownership boundary.
- v0.3 documentation MUST retain the verified manual update procedure.

### Constraints

- The technical choices supplied to `establish-technical-baseline` are inputs, not permission to invent product or domain architecture.
- Only a decision owner can accept RFC or ARP outcomes and only the user can approve issue publication or disposition of review findings.
- Investigation may use disposable probes, but permanent tests and fixes are executable project work.
- Release-manifest inventory and dependency declarations must include all new skills without weakening deterministic release verification.
- A safe automatic updater requires immutable planning, staged replacement, journaling, rollback, interruption recovery, and safe replacement of the executing lifecycle command; these guarantees should not be shipped partially.

### Assumptions

- v0.2 consumers can use installed verification and reviewed manual updates while the installed population remains small.
- The six workflows will be used more often than cross-version update automation in the next release cycle.
- Real v0.2 adoption will provide better evidence for eventual update compatibility and recovery requirements.

### Preferences

- Prefer semantic workflow value over speculative maintenance machinery.
- Prefer evidence and explicit authority over generic “best practice” advice.
- Prefer narrow review findings and regression checks over agents silently fixing work under review.
- Prefer project conventions and approved locations over new global configuration fields.
- Prefer complete update safety later over a partial updater in v0.3.

## Non-goals

- Reusable update planning or distribution-managed file replacement.
- Transaction journals, backups, rollback, interruption recovery, or lifecycle self-update.
- Public migration tooling or legacy baseline manifests.
- Configuration schema 3.
- Automatic conflict merging, schema migration, or artifact migration.
- Selecting a project's programming language, framework, cloud, or database.
- Product-dependent architecture before product intent and domain constraints are known.
- Silent implementation fixes during investigation or review.
- Mandatory standalone commits containing failing regression tests.

## Open questions

None.

## Options

### Option A: Add six foundation and feedback skills; defer update automation

Ship the six proposed skills, retain schema 2 and manual updates, and revisit automation from v0.2 adoption evidence.

Advantages:

- closes concrete gaps at project inception and after implementation;
- expands the toolkit's reusable semantic value;
- avoids coupling new workflows to one technology or harness;
- keeps update safety guarantees honest; and
- allows eventual updater design to reflect real installations.

Disadvantages:

- consumers continue to perform reviewed manual updates;
- ARP-0004's provisional v0.3 update expectation moves again; and
- six skills require careful boundary and routing design.

### Option B: Make reusable updates the v0.3 theme

Implement immutable cross-version plans, replacement transactions, rollback, recovery, and lifecycle self-update before adding workflows.

Advantages:

- fulfills the full lifecycle direction originally explored in RFC-0002;
- establishes strong maintenance guarantees before adoption grows; and
- reduces repeated manual update work.

Disadvantages:

- prioritizes a failure surface with little current usage evidence;
- delays more frequently useful semantic operations; and
- requires broad failure-injection and compatibility work.

### Option C: Mix new skills with a partial updater

Add a smaller skill set and only update comparison or replacement behavior.

Advantages:

- advances both themes; and
- may reduce some manual update steps.

Disadvantages:

- fragments the release outcome;
- risks presenting incomplete update behavior as safe; and
- leaves rollback and recovery obligations unresolved.

### Option D: Keep v0.2 behavior unchanged

Publish no new workflow or lifecycle capability.

Advantages:

- incurs no implementation risk; and
- allows more time to observe v0.2 adoption.

Disadvantages:

- leaves identified workflow gaps unresolved; and
- provides no meaningful v0.3 release outcome.

## Recommendation

Choose Option A.

The six skills form a coherent path: establish a sound technical foundation, triage incoming work, diagnose failures, capture regressions, review implementation conformance, and close initiatives honestly. The release remains focused by excluding lifecycle changes and schema migration. Update automation should be reprioritized when there are multiple active consumer repositories, external consumers, repeated manual-update failures, material local skill customizations, or update effort becomes an adoption barrier.

## Resolution

Accepted by the decision owner on 2026-08-24. v0.3 adopts Option A: add `establish-technical-baseline`, `triage-issue`, `investigate-failure`, `capture-regression`, `review-implementation`, and `close-initiative`; retain schema 2 and reviewed manual updates; and make no transactional lifecycle changes.

Reusable update planning, replacement, rollback, recovery, and self-update are provisionally deferred to v0.4. The trigger conditions in the recommendation can reprioritize that work earlier. The roadmap decision is recorded in [ARP-0005](../decisions/ARP-0005-focus-v0.3-on-project-feedback-workflows.md). Detailed skill contracts and implementation slicing remain separate work.
