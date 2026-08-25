---
id: ISSUE-0051
title: "Correct discovery semantics and inspect backends conditionally"
kind: "implementation"
status: resolved
created: 2026-08-25
assignee: "pi"
parent: "ISSUE-0050-streamline-deterministic-consumer-configuration.md"
blocked_by:
labels: ["lifecycle","configuration"]
---
# Correct discovery semantics and inspect backends conditionally

## Parent

Streamline deterministic consumer configuration

## What to build

Make installation inspection distinguish manifest-verified discovery evidence from model invocation eligibility, and defer external backend inspection until the user considers that backend.

## Acceptance criteria

- [ ] Manifest format 2 gives every skill exactly one `model_invocation` value: `enabled` or `manual`, derived from validated skill frontmatter.
- [ ] Installed `inspect` reports installed, model-invocable, and manual-invocation skill names without claiming actual runtime prompt visibility.
- [ ] Skills with `disable-model-invocation: true` pass complete installation and Pi discovery-root inspection while absent from the model-visible skill prompt.
- [ ] Pi guidance treats an integrity-checked project `.agents/skills/` installation that existed at startup as discovery evidence and requests restart or rediscovery only for post-startup installation or unavailable manual commands.
- [ ] The workflow no longer requires every installed directory to appear in prompt-visible inventory.
- [ ] Initial inspection covers only workspace/version control, existing workflow guidance and artifact conventions, distribution integrity, and project structure before asking the project/profile question.
- [ ] GitHub and Bear inspection occurs only when each backend is considered; local-only setup invokes neither `gh` nor `bearcli`.
- [ ] Authoritative configuration requirements and discovery documentation reflect the corrected phases.

## Blocked by

None.

## Out of scope

Consumer plan/apply, skill installation, runtime prompt introspection, and backend mutation.

## Comments
## Resolution

Corrected discovery semantics and provider inspection order. Manifest format 2 now derives an immutable `model_invocation` value from validated skill frontmatter for every skill. Installed inspection reports separate `installed`, `model_invocable`, and `manual_invocation` sets in JSON and human output; all seven `disable-model-invocation: true` skills pass recursive Pi `.agents/skills/` discovery-root integrity checks without being treated as prompt-visible. `configure-workflows` now explicitly distinguishes installation, discovery, invocation eligibility, and runtime prompt state; requests restart or rediscovery only after post-startup installation or an unavailable manual command; and no longer requires prompt visibility. Exploration is split into provider-neutral initial inspection followed by a project/profile question and conditional GitHub or Bear inspection. Local-only inspection is regression-tested with failing `gh` and `bearcli` sentinels and invokes neither. Updated the authoritative routing specification, manifest/configuration/verification/fresh/adoption guidance, starting flow, and changelog. `scripts/verify.sh` passes with 137 tests.
