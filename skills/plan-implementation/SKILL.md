---
name: plan-implementation
description: Decompose an approved specification or settled plan into dependent, executable vertical-slice issues using the configured issue-tracker backend.
disable-model-invocation: true
license: MIT
---

# Plan Implementation

Read `.agents/workflows.yaml` and `docs/agents/issue-tracker.md`. If backend instructions are absent, stop and ask the user to run `configure-workflows`.

## Gather context

Read the complete source specification, RFC resolution, initiative map, or conversation. Read relevant domain docs and accepted ARPs. Explore the codebase enough to identify existing seams and necessary prefactoring.

Do not proceed while implementation-blocking ambiguity remains. Send it to `clarify-intent`, `develop-rfc`, or `plan-initiative` as appropriate.

## Draft vertical slices

Each issue should:

- deliver a narrow but complete path through the affected system;
- be independently demonstrable or verifiable;
- fit one fresh agent session;
- state observable acceptance criteria; and
- identify only dependencies that genuinely gate starting it.

Prefer tracer-bullet behavior over separate database, backend, frontend, and test tickets. Put enabling prefactors first when they make subsequent changes safer.

### Wide refactors

When one mechanical change cannot land as a vertical slice, use expand-contract:

1. add the new form beside the old;
2. migrate callers in independently safe batches;
3. remove the old form after all migrations; and
4. use an integration branch only when batches cannot remain independently green.

## Confirm

Present a numbered draft with title, blockers, delivered behavior, and acceptance criteria. Ask whether granularity and dependencies are correct. Iterate until approved.

## Publish

Create issues through the configured backend in dependency order, then add parent and blocking relationships. Use [the issue template](references/issue-template.md).

Do not add brittle file-by-file instructions or speculative implementation detail. Link the source specification. Do not close or rewrite the parent artifact.
