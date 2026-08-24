---
name: configure-project
description: Configure a repository to use these workflows by selecting issue tracking, artifact paths, and optional capabilities. Use once when adopting the workflow kit in a new or existing project.
disable-model-invocation: true
license: MIT
---

# Configure Project

Inspect first, propose second, and write only after confirmation. Installation must not silently migrate existing artifacts.

## Explore

From the repository root, inspect:

- Git remotes and whether the project uses GitHub Issues;
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

Ask one decision at a time. Do not ask for facts available in the repository.

## Confirm

Show a dry run containing:

1. `.agents/workflows.yaml`, based on [the example](references/workflow-config.example.yaml);
2. the selected issue-backend instructions;
3. `docs/agents/workflows.md`;
4. the concise agent-instructions block; and
5. every directory or file that would be created or changed.

Wait for explicit approval.

## Write

- Write `.agents/workflows.yaml` as the canonical configuration.
- Copy the selected bundled adapter, [GitHub](references/issue-tracker-github.md) or [local Markdown](references/issue-tracker-local-markdown.md), to `docs/agents/issue-tracker.md`. Both implement the bundled [backend contract](references/issue-tracker-contract.md).
- Write `docs/agents/workflows.md` with the artifact authority table, configured paths, optional features, and a pointer to the issue backend.
- Add or update a short `## Engineering workflows` section in the existing agent-guidance file. Use [the seed block](references/agents-section.md). Do not replace surrounding instructions.
- Create `docs/agents/`, but create optional artifact and local-issue directories only when their first artifact is needed.

Finish by listing the written files and the workflows that now use them.
