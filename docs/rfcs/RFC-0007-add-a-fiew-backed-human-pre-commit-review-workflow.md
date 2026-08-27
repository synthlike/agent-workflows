<!-- agent-workflows-record
{"archived":false,"created":"2026-08-27T18:28:23Z","id":"RFC-0007","modified":"2026-08-27T18:34:15Z","record_type":"rfcs","title":"Add a Fiew-backed human pre-commit review workflow"}
-->
---
id: RFC-0007
title: Add a Fiew-backed human pre-commit review workflow
status: draft
authors: [synthlike]
created: 2026-08-27
decision_owner: synthlike
related_arps: []
---

# Add a Fiew-backed human pre-commit review workflow

## Summary

Consider a reusable `request-human-review` skill that asks a human to review the current uncommitted change through Fiew after implementation and verification but before commit approval.

## Motivation

The current workflows can review implementation intent and ask before committing, but they do not provide a structured human review checkpoint with threaded discussion. [Fiew](https://github.com/synthlike/fiew) already provides commands to create, open, inspect, and reply to a review.

## Requirements and constraints

- Run only after implementation and normal verification are complete.
- Bind the review to the current HEAD and working-tree digest.
- Ask before creating the review because `fiew review start --name pre-commit` persists review state.
- Treat review and thread identifiers as opaque values returned by Fiew.
- Pause until the human explicitly says the review is complete.
- After that signal, run `fiew review show <review-id>`.
- Treat exit code `0` as no unresolved threads and exit code `1` as unresolved comments that must be addressed.
- Prepare exact reply bodies for approval before running `fiew review reply <review-id> <thread-id> --body-file <file>`.
- Rerun project verification after addressing comments.
- Any code change invalidates the reviewed working-tree digest and requires renewed human review.
- Require separate approval before commit even after review succeeds.
- Keep Fiew as the owner of review storage rather than duplicating review threads in Markdown.

## Non-goals

- Replacing the existing agent-driven `review-implementation` conformance workflow.
- Automatically committing after a successful review.
- Treating an untouched review with no threads as implicit human approval.
- Encoding Fiew identifiers or storage details into semantic project records.

## Open questions

- What stable or machine-readable output does `fiew review start` provide for extracting the review ID?
- How should the workflow distinguish exit code `1` for unresolved threads from operational failures?
- Does Fiew expose the reviewed HEAD and working-tree digest, or must the skill bind and compare them itself?
- How should renewed review work after code changes: update the existing review or create a new review?
- Should Fiew integration be an optional review backend configured by the consumer project?

## Options

### Option A: Add a standalone `request-human-review` skill

Keep human review orchestration separate from agent conformance review. The skill uses a concrete Fiew backend/reference document and can be invoked before commit when desired.

### Option B: Extend `review-implementation`

Add Fiew as an optional final phase of the existing skill. This reduces the number of workflows but mixes agent assessment with human review transport and approval state.

### Option C: Keep review outside agent workflows

Continue invoking Fiew manually. This avoids integration work but cannot enforce digest binding, thread resolution, re-verification, or the pre-commit gate consistently.

## Recommendation

Start with Option A. A standalone semantic workflow keeps human review distinct from agent conformance review. Initially require an explicit human “review complete” signal before interpreting `fiew review show`; later Fiew may provide a machine-readable completed-review state.

## Resolution

Unresolved draft. No implementation issue or accepted decision has been created.
