---
name: configure-project
description: Configure a repository to use these workflows by selecting issue tracking, artifact paths, and optional capabilities. Use once when adopting the workflow kit in a new or existing project.
disable-model-invocation: true
license: MIT
---

# Configure Project

Inspect first, propose second, and write only after confirmation. Installation must not silently migrate existing artifacts.

## Lifecycle assets

Release identity, complete skill inventory, dependencies, and file integrity are defined by the embedded [distribution manifest](references/distribution-manifest.json). Use the deterministic [lifecycle command](references/lifecycle.py) for manifest inspection, closure, and installed verification; keep human intent, dry-run review, write approval, and harness discovery confirmation in this skill.

## Explore

From the repository root, inspect:

- Git remotes and whether the project uses GitHub Issues;
- the workflows explicitly selected by the user and the exact skill directories discovered by the harness;
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
- meeting notes disabled unless requested; and
- a plain-language documentation style unless the project already defines one: use active voice, short sentences, explicit references, established domain terms, and one action per procedural step; avoid idioms, unnecessary synonyms, and ambiguous pronouns.

Ask one decision at a time. Do not ask for facts available in the repository. If distribution identity cannot be established from installation metadata or the repository, ask for it rather than proposing a mutable value such as a branch name, `latest`, or `unreleased`.

Use the lifecycle command to calculate the selected closure and inspect the exact harness-discovered directories. Require the complete distribution, even when the user explicitly selects only a subset of workflows. If any skill is absent, stop and list every missing skill. Ask the user to complete installation through their external installer or an intact manual copy, then confirm harness discovery and inspect again. Never create, replace, or remove a skill directory.

## Confirm

Show a dry run containing:

1. exact distribution identity;
2. user-selected workflows, calculated closure, and the complete discovered skill inventory;
3. any missing, unexpected, duplicate, incomplete, or modified skill and every blocking conflict;
4. `.agents/workflows.yaml`, based on [the example](references/workflow-config.example.yaml), with schema 2, exact distribution identity, selected workflows, and complete discovered skill-path inventory;
5. the selected issue-backend instructions;
6. `docs/agents/workflows.md`, including the preserved project writing policy or the default plain-language documentation style;
7. the concise agent-instructions block; and
8. every other directory or file that would be created or changed.

Wait for explicit approval.

## Write

- Never write project configuration while the complete distribution is absent or fails integrity inspection.
- Ask the harness to rediscover skills after external installation changes. Continue only after it confirms every distributed skill at its repository-contained path.
- Write `.agents/workflows.yaml` as the canonical schema-2 configuration. Never write a placeholder or mutable distribution version.
- Copy the selected bundled adapter, [GitHub](references/issue-tracker-github.md) or [local Markdown](references/issue-tracker-local-markdown.md), to `docs/agents/issue-tracker.md`. Both implement the bundled [backend contract](references/issue-tracker-contract.md).
- Write `docs/agents/workflows.md` with the artifact authority table, configured paths, optional features, a pointer to the issue backend, and a `## Documentation style` section. Preserve an existing project policy. Otherwise write: "Write clear, direct documentation. Prefer active voice, short sentences, explicit references, and established domain terms. Avoid idioms, unnecessary synonyms, and ambiguous pronouns. Use one action per procedural step."
- Add or update a short `## Engineering workflows` section in the existing agent-guidance file. Use [the seed block](references/agents-section.md). Do not replace surrounding instructions.
- Create `docs/agents/`, but create optional artifact and local-issue directories only when their first artifact is needed.

Run installed lifecycle verification against the exact rediscovered directories. Finish only when it passes, then list created skill directories, written configuration and guidance, selected workflows, and calculated closure.
