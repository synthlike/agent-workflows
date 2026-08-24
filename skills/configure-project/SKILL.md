---
name: configure-project
description: Configure a repository to use these workflows by selecting issue tracking, artifact paths, and optional capabilities. Use once when adopting the workflow kit in a new or existing project.
disable-model-invocation: true
license: MIT
---

# Configure Project

Inspect first, propose second, and write only after confirmation. Installation must not silently migrate existing artifacts.

## Lifecycle assets

v0.2 release identity, dependencies, and file integrity are defined by the bundled [distribution manifest](references/distribution-manifest.json). Use the deterministic [lifecycle command](references/lifecycle.py) for manifest, closure, bundle, and installed-verification operations as they become available; keep human intent and write approval in this skill.

## Explore

From the repository root, inspect:

- Git remotes and whether the project uses GitHub Issues;
- the installed distribution source and exact release version or immutable commit SHA;
- `AGENTS.md`, `CLAUDE.md`, or equivalent agent guidance;
- `.agents/workflows.yaml` and `docs/agents/`;
- existing domain glossaries or context maps;
- directories containing ADRs, ARPs, RFCs, specifications, plans, or meeting notes;
- local issue conventions such as `.project/` or `.scratch/`; and
- monorepo signals relevant to domain-document layout.

## Recommend

Prefer existing conventions. For a new project, recommend:

- GitHub tracking when a GitHub remote and active issue workflow exist;
- otherwise committed local Markdown under `.project/`;
- domain docs under `docs/domain/`;
- ARPs under `docs/decisions/`;
- RFCs under `docs/rfcs/`;
- specifications under `docs/specifications/`; and
- meeting notes disabled unless requested.

Ask one decision at a time. Do not ask for facts available in the repository. If distribution identity cannot be established from installation metadata or the repository, ask for it rather than proposing a mutable value such as a branch name, `latest`, or `unreleased`.

## Confirm

Show a dry run containing:

1. `.agents/workflows.yaml`, based on [the example](references/workflow-config.example.yaml), with `distribution.source` and an exact release version or immutable commit SHA;
2. the selected issue-backend instructions;
3. `docs/agents/workflows.md`;
4. the concise agent-instructions block; and
5. every directory or file that would be created or changed.

Wait for explicit approval.

## Write

- Write `.agents/workflows.yaml` as the canonical configuration. Never write a placeholder or mutable distribution version.
- Copy the selected bundled adapter, [GitHub](references/issue-tracker-github.md) or [local Markdown](references/issue-tracker-local-markdown.md), to `docs/agents/issue-tracker.md`. Both implement the bundled [backend contract](references/issue-tracker-contract.md).
- Write `docs/agents/workflows.md` with the artifact authority table, configured paths, optional features, and a pointer to the issue backend.
- Add or update a short `## Engineering workflows` section in the existing agent-guidance file. Use [the seed block](references/agents-section.md). Do not replace surrounding instructions.
- Create `docs/agents/`, but create optional artifact and local-issue directories only when their first artifact is needed.

Finish by listing the written files and the workflows that now use them.
