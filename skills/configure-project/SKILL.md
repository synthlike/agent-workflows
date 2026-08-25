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

- Git remotes, whether the project uses GitHub Issues, authenticated `github.com` accounts, and the currently active account;
- the workflows explicitly selected by the user and the exact skill directories discovered by the harness;
- the installed distribution source and exact release version or immutable commit SHA;
- `AGENTS.md`, `CLAUDE.md`, or equivalent agent guidance;
- `.agents/workflows.yaml` and `docs/agents/`;
- existing domain glossaries or context maps;
- directories containing ADRs, ARPs, RFCs, specifications, plans, meeting notes, research, questionnaires, technical baselines, prototypes, or handoffs;
- local issue conventions such as `.project/` or `.scratch/`;
- monorepo signals relevant to domain-document layout; and
- the nature of the project and how people and agents will collaborate on it.

## Recommend

Prefer existing conventions. For a new project, recommend:

- GitHub tracking when a GitHub Cloud remote and active issue workflow exist, `gh` authentication and repository write access pass preflight, and native sub-issues and dependencies are acceptable;
- otherwise committed local Markdown under `.project/`;
- domain docs under `docs/domain/`;
- ARPs under `docs/decisions/`;
- RFCs under `docs/rfcs/`;
- specifications under `docs/specifications/`;
- meeting notes disabled unless requested;
- research enabled under `docs/research/`;
- questionnaires enabled under `docs/questionnaires/`;
- technical baselines enabled under `docs/engineering/`;
- retained prototypes disabled, with `docs/prototypes/` reserved if enabled;
- durable handoffs disabled, with `.agents/handoffs/` reserved if enabled; and
- a plain-language documentation style unless the project already defines one: use active voice, short sentences, explicit references, established domain terms, and one action per procedural step; avoid idioms, unnecessary synonyms, and ambiguous pronouns.

Ask what kind of project this is and how people and agents will collaborate on it. Combine that answer with repository evidence to recommend each capability individually, explain the reason, and confirm one decision at a time. Do not use rigid project-type profiles. An `enabled: false` artifact capability prohibits repository writes without approval but does not prohibit temporary or external output. Do not ask for facts available in the repository. If distribution identity cannot be established from installation metadata or the repository, ask for it rather than proposing a mutable value such as a branch name, `latest`, or `unreleased`.

When GitHub is considered, list authenticated account names and identify the active account without exposing tokens. Ask which login should own backend operations, even when an account is already active, and record that login in `issue_tracker.login`. When several accounts exist, never infer the intended identity from the active account alone. If the selected account is not active, ask the user to run `gh auth switch --hostname github.com --user LOGIN`, wait for confirmation, and recheck; never change global authentication silently.

When GitHub is selected, run the bundled `github-issues.py --login LOGIN preflight` and generate a label plan with the same explicit login. Stop if the repository is not on GitHub Cloud, Issues is disabled, authentication fails, write permission is absent, or native relationships are unavailable. Show every proposed `workflow:*` label creation or update and apply only the exact reviewed plan after approval. Do not fall back to task lists, body-text dependencies, or unreviewed labels.

Use the lifecycle command to calculate the selected closure and inspect the exact harness-discovered directories. Require the complete distribution, even when the user explicitly selects only a subset of workflows. If any skill is absent, stop and list every missing skill. Ask the user to complete installation through their external installer or an intact manual copy, then confirm harness discovery and inspect again. Never create, replace, or remove a skill directory.

## Confirm

Show a dry run containing:

1. exact distribution identity;
2. user-selected workflows, calculated closure, and the complete discovered skill inventory;
3. any missing, unexpected, duplicate, incomplete, or modified skill and every blocking conflict;
4. `.agents/workflows.yaml`, based on [the example](references/workflow-config.example.yaml), with schema 2, exact distribution identity, selected workflows, and complete discovered skill-path inventory;
5. the selected issue-backend instructions, plus the chosen GitHub login, helper destination, preflight result, and complete label plan when GitHub is selected;
6. `docs/agents/workflows.md`, including the preserved project writing policy or the default plain-language documentation style;
7. the concise agent-instructions block; and
8. every other directory or file that would be created or changed.

Wait for explicit approval.

## Write

- Never write project configuration while the complete distribution is absent or fails integrity inspection.
- Ask the harness to rediscover skills after external installation changes. Continue only after it confirms every distributed skill at its repository-contained path.
- Write `.agents/workflows.yaml` as the canonical schema-2 configuration. Never write a placeholder or mutable distribution version.
- Copy the selected bundled adapter, [GitHub](references/issue-tracker-github.md) or [local Markdown](references/issue-tracker-local-markdown.md), to `docs/agents/issue-tracker.md`. Both implement the bundled [backend contract](references/issue-tracker-contract.md).
- For GitHub, also copy the bundled `references/github-issues.py` helper to `docs/agents/github-issues.py`, then apply the exact approved label plan. Do not create or update labels before approval. For local Markdown, do not write the GitHub helper.
- Write `docs/agents/workflows.md` with the artifact authority table, configured paths, optional features, a pointer to the issue backend, and a `## Documentation style` section. Preserve an existing project policy. Otherwise write: "Write clear, direct documentation. Prefer active voice, short sentences, explicit references, and established domain terms. Avoid idioms, unnecessary synonyms, and ambiguous pronouns. Use one action per procedural step."
- Add or update a short `## Engineering workflows` section in the existing agent-guidance file. Use [the seed block](references/agents-section.md). Do not replace surrounding instructions.
- Create `docs/agents/`, but create optional artifact and local-issue directories only when their first artifact is needed.

Run installed lifecycle verification against the exact rediscovered directories. Finish only when it passes, then list created skill directories, written configuration and guidance, selected workflows, and calculated closure.
