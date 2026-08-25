---
name: configure-workflows
description: Configure a consumer workspace to use these workflows by selecting explicit record routes, backend instances, and optional capabilities. Use once when adopting the workflow kit in a new or existing project.
disable-model-invocation: true
license: MIT
---

# Configure Workflows

Inspect first, propose second, and write only after confirmation. Installation must not silently migrate existing artifacts.

## Lifecycle assets

Release identity, complete skill inventory, dependencies, and file integrity are defined by the embedded [distribution manifest](references/distribution-manifest.json). Use the deterministic [lifecycle command](references/lifecycle.py) for manifest inspection, closure, plan generation, transactional apply, and installed verification; keep human intent, plan review, one local-file approval, provider-specific approvals, and harness discovery confirmation in this skill.

## Explore

### Harness discovery

Distinguish installation, discovery, and model invocation eligibility. A skill with `disable-model-invocation: true` may be discovered by the harness while absent from the model's available-skills prompt. Do not classify that skill as missing solely because it is absent from the prompt. Manifest `model_invocation` records static invocation policy, not actual runtime prompt contents.

For Pi, a complete integrity-checked installation under the project `.agents/skills/` discovery root is sufficient discovery evidence when the skills existed at startup. Request a restart or rediscovery only when files were installed after startup or a manual `/skill:name` command is unavailable. Other harnesses may supply their exact discovered directories through their supported discovery seam.

### Initial inspection

From the consumer workspace root, inspect only:

- whether the workspace uses Git, another version-control system, or no version control, and the discovered workspace boundary;
- the complete installed distribution integrity, invocation policy, source, exact release version or immutable commit SHA, and selected-workflow intent;
- `AGENTS.md`, `CLAUDE.md`, or equivalent agent guidance;
- `.agents/workflows.yaml`, `docs/agents/records.md`, and generated assets under `docs/agents/backends/`;
- existing domain glossaries, context maps, artifact directories, local issue conventions, and other record-location conventions; and
- project structure, including monorepo signals relevant to record layout.

Then begin one project/profile question sequence: ask what kind of project this is and how people and agents will collaborate on it, and gather only intent that remains unresolved after inspection. Use the answers to identify a local, GitHub, mixed, or Bear-backed profile before any provider-specific inspection. Do not repeat questions for facts or choices already resolved.

### Backend inspection

Inspect only backends that the user is considering:

- for GitHub, inspect remotes when relevant, authenticated `github.com` accounts, the active account, repository capabilities, and managed labels; and
- for Bear, inspect the explicitly selected `bearcli` executable, project workspace tag, and read-only MCP capabilities.

For a local-only profile, do not invoke `gh`, `bearcli`, or another external-backend tool.

## Recommend

Prefer existing conventions. For a new project, recommend:

- GitHub persistence for any suitable semantic records when an explicit GitHub Cloud repository and login pass identity and capability preflight; use native sub-issues and dependencies when `issues` is routed there;
- Bear persistence only for non-issue semantic records when an explicit absolute `bearcli` command and project workspace pass read-only capability preflight and the installed Bear adapter declares the complete record contract;
- otherwise local Markdown, committed when the workspace uses a commit-based version-control system;
- domain docs under `docs/domain/`;
- ARPs under `docs/decisions/`;
- RFCs under `docs/rfcs/`;
- specifications under `docs/specs/`;
- meeting notes disabled unless requested;
- research enabled under `docs/research/`;
- questionnaires enabled under `docs/questionnaires/`;
- technical baselines enabled under `docs/engineering/`;
- product problem framing enabled under `docs/product/`;
- retained prototypes disabled, with `docs/prototypes/` reserved if enabled;
- durable handoffs disabled, with `.agents/handoffs/` reserved if enabled; and
- a plain-language documentation style unless the project already defines one: use active voice, short sentences, explicit references, established domain terms, and one action per procedural step; avoid idioms, unnecessary synonyms, and ambiguous pronouns.

Git is not required. Do not ask whether Git exists when inspection already answers that question. When no version-control system is detected, ask whether the workspace is intentionally unversioned or whether the user intends to initialize or identify a version-controlled root. Explain that unversioned workspaces have no commit checkpoint or version-control history, but never initialize, change, or configure version control without approval. When another version-control system is present, preserve its conventions and use its landing terminology rather than assuming Git.

Use the project and collaboration answer from initial inspection. Profile questions may offer all-local, all-GitHub, mixed local/GitHub, or Bear-for-non-issues with a complete local/GitHub issue backend as shortcuts, but expand every answer into explicit routes for `issues`, `domain`, `arps`, `rfcs`, `specs`, `meetings`, `research`, `questionnaires`, `technical_baselines`, `problem_framing`, `prototypes`, and `handoffs`. Show and confirm the enabled state, named backend, and complete destination for every route, including disabled routes. Combine the answer with repository evidence to recommend each capability individually and explain the reason. An `enabled: false` route prohibits repository writes without approval but does not prohibit temporary or external output. Do not ask for facts available in the repository. If distribution identity cannot be established from installation metadata or the repository, ask for it rather than proposing a mutable value such as a branch name, `latest`, or `unreleased`.

When GitHub is considered, list authenticated account names and identify the active account without exposing tokens. Ask which login should own backend operations, even when an account is already active, and record the explicit repository and login in the named GitHub backend instance. When several accounts exist, never infer the intended identity from the active account alone. If the selected account is not active, ask the user to run `gh auth switch --hostname github.com --user LOGIN`, wait for confirmation, and recheck; never change global authentication silently.

For every GitHub backend instance, run bundled `references/backends/record-store/github.py --repo OWNER/REPO --login LOGIN --backend INSTANCE preflight` before recommending or asking approval for any route. Confirm the actual API identity, GitHub Cloud repository, enabled Issues, write permission, complete record contract, and—when `issues` uses the instance—native sub-issues and dependencies plus the complete issue contract. Stop on any missing capability or identity mismatch.

For every Bear backend instance, run bundled `references/backends/record-store/bear.py --command ABSOLUTE_BEARCLI --workspace WORKSPACE preflight` before recommending or asking approval for a non-issue route. Confirm the `bearcli` identity, exact single-workspace scope, required MCP tools and schemas, and provider record capabilities. The preflight is read-only and does not provision a tag or note. Stop if provider preflight fails or the immutable adapter declaration lacks the routed type or common operation. Never route `issues` to Bear or add a harness-specific MCP registration.

Generate a label-plan format 2 document with the same explicit repository and login. Show every proposed `workflow:record:*` and `workflow:issue:*` creation or update and apply only the exact reviewed plan after approval. Label provisioning is a separate external mutation; never apply it merely because routes were approved. Do not fall back to task lists, body-text dependencies, or unreviewed labels.

Use the lifecycle command to calculate the selected closure and inspect the integrity-checked installed directories supplied through the harness discovery seam. Require the complete distribution, even when the user explicitly selects only a subset of workflows. Treat manifest-declared manual-invocation skills as installed when their discovered directories pass integrity checks; do not require them to appear in the model prompt. If any skill directory is absent, stop and list every missing skill. Ask the user to complete installation through their external installer or an intact manual copy, then request restart or rediscovery only when the files were added after harness startup or a manual command remains unavailable. Never create, replace, or remove a skill directory.

## Confirm

Normalize the confirmed question sequence against the strict [answer schema](references/consumer-answers.schema.json), including expected prior state for every managed target. Invoke installed `lifecycle.py plan-consumer`; do not compose YAML, Markdown, root guidance, or backend assets manually.

Present the one complete canonical plan with:

1. its exact `sha256` digest and consumer root;
2. immutable distribution identity, user-selected workflows, calculated closure, invocation policy, and complete discovered inventory;
3. every generated text byte and copied backend source/destination hash;
4. expected prior hash or absence for every target;
5. all twelve explicit routes, including disabled routes, and exactly the backend assets used;
6. managed parent directories to create and lazy record destinations deliberately left absent;
7. detected version-control state and landing-checkpoint behavior; and
8. applicable read-only provider preflight evidence and external provisioning plans.

For local consumer files, ask once whether to apply this exact digest. Do not request separate approval per file or directory. If intent, installation, target state, provider evidence, or plan bytes change, discard the plan, regenerate it, and request approval for the new digest. Plan generation performs no consumer or provider mutation.

GitHub label provisioning is not included in this approval. When GitHub is considered, present its exact label plan separately and request a separate approval immediately before stale-safe label application. Bear preflight remains read-only and has no provisioning step.

## Write

- Never write configuration while the complete distribution is absent or fails integrity inspection.
- After approval, invoke installed `lifecycle.py apply-consumer` with the reviewed plan file and exact approved digest. Do not use general editing or copy tools to reproduce planned local files.
- Let apply recheck canonical plan bytes, release and consumer identity, complete installed inventory, target and source hashes, destination containment, complete target set, and directory intent; stage every output; write only changed planned targets; run installed `verify-consumer`; and roll back caught failures.
- Treat any stale-state, validation, write, rollback, or verification error as a stop. Reinspect and replan rather than repairing generated files by hand.
- Never install, replace, remove, or modify skill directories. Request restart or rediscovery only after post-startup external installation or an unavailable manual command.
- Do not require or initialize Git. Preserve the detected version-control system and approved consumer root.
- Do not create local record destinations, move existing records, or mutate backend records as part of apply. Disabled and unused destinations remain lazy.
- Do not generate legacy issue-tracker assets. The plan must contain only the shared contract and guidance/helper pairs for backend types used by routes.
- After successful local apply, perform no external mutation implicitly. Apply an exact GitHub label plan only after its separate approval and fresh stale-state check. Bear inspection remains read-only.

Finish only after apply reports successful installed verification. Report the approved digest, changed and unchanged files, created managed directories, deliberately absent record destinations, selected workflows and closure, detected version-control state, landing checkpoint, and any separately completed provider operation.
