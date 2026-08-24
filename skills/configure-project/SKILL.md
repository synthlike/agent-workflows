---
name: configure-project
description: Configure a repository to use these workflows by selecting issue tracking, artifact paths, and optional capabilities. Use once when adopting the workflow kit in a new or existing project.
disable-model-invocation: true
license: MIT
---

# Configure Project

Inspect first, propose second, and write only after confirmation. Installation must not silently migrate existing artifacts.

## Lifecycle assets

v0.2 release identity, dependencies, and file integrity are defined by the bundled [distribution manifest](references/distribution-manifest.json). Use the deterministic [lifecycle command](references/lifecycle.py) for manifest, closure, bundle, fresh-install planning and apply, and installed verification; keep human intent, dry-run review, write approval, and harness discovery confirmation in this skill.

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

Use the lifecycle command to calculate the selected closure and inspect the exact harness-discovered directories. If dependencies are missing, obtain the matching current-release bundle by local path or HTTPS URL and generate a fresh-install plan. Default each missing skill beside discovered `configure-project`; ask only about desired destination overrides or blocking conflicts. Never propose replacing or removing an existing skill directory.

## Confirm

Show a dry run containing:

1. release-bundle identity and SHA-256 when missing skills must be added;
2. user-selected workflows, calculated closure, discovered and unexpected skills, and missing skills;
3. every skill source and repository-contained destination, including overrides;
4. every skill-directory create action and blocking conflict;
5. `.agents/workflows.yaml`, based on [the example](references/workflow-config.example.yaml), with schema 2, exact distribution identity, selected workflows, and complete discovered skill-path inventory;
6. the selected issue-backend instructions;
7. `docs/agents/workflows.md`, including the preserved project writing policy or the default plain-language documentation style;
8. the concise agent-instructions block; and
9. every other directory or file that would be created or changed.

Wait for explicit approval.

## Write

- For an approved missing-skill plan, invoke lifecycle apply with the exact plan and matching bundle. It may create only absent skill directories. If apply fails, stop and report its cleanup guidance.
- Ask the harness to rediscover skills. Continue only after it confirms every skill in the closure at the planned paths.
- Write `.agents/workflows.yaml` as the canonical schema-2 configuration. Never write a placeholder or mutable distribution version.
- Copy the selected bundled adapter, [GitHub](references/issue-tracker-github.md) or [local Markdown](references/issue-tracker-local-markdown.md), to `docs/agents/issue-tracker.md`. Both implement the bundled [backend contract](references/issue-tracker-contract.md).
- Write `docs/agents/workflows.md` with the artifact authority table, configured paths, optional features, a pointer to the issue backend, and a `## Documentation style` section. Preserve an existing project policy. Otherwise write: "Write clear, direct documentation. Prefer active voice, short sentences, explicit references, and established domain terms. Avoid idioms, unnecessary synonyms, and ambiguous pronouns. Use one action per procedural step."
- Add or update a short `## Engineering workflows` section in the existing agent-guidance file. Use [the seed block](references/agents-section.md). Do not replace surrounding instructions.
- Create `docs/agents/`, but create optional artifact and local-issue directories only when their first artifact is needed.

Run installed lifecycle verification against the exact rediscovered directories. Finish only when it passes, then list created skill directories, written configuration and guidance, selected workflows, and calculated closure.
