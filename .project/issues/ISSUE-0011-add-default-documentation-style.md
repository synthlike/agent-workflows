---
id: ISSUE-0011
title: Add a default documentation style
kind: task
status: resolved
created: 2026-08-24
assignee: synthlike
parent:
blocked_by: []
labels: [documentation, v0.2]
---

# Add a default documentation style

## What to build

Give fresh consumer projects concise plain-language guidance for workflow-generated documentation. Preserve an existing project's writing policy and let consumers replace the default without editing installed skills.

## Acceptance criteria

- [x] `configure-workflows` recommends the default only when the project has no established writing policy.
- [x] Generated `docs/agents/workflows.md` includes a `## Documentation style` section with direct, actionable guidance.
- [x] Customization documentation identifies the guidance as project-overridable and does not claim ASD-STE100 compliance.
- [x] The real fresh-install smoke scenario generates the default section.
- [x] The release manifest is regenerated and all verification passes.

## Blocked by

None.

## Out of scope

- Mandatory ASD-STE100 compliance.
- A controlled-vocabulary validator or documentation linter.
- A new workflow-configuration schema field for writing style.

## Comments

2026-08-24 — synthlike: This issue was created after implementation began. The change was initially treated as a small direct documentation improvement, but repository policy requires executable work to be tracked as an issue. Recording it retroactively corrects that process omission; no RFC was needed because the default and project-override boundary were resolved before implementation.

## Resolution

Resolved on 2026-08-24. `configure-workflows` now preserves existing writing policy or adds a concise plain-language default to `docs/agents/workflows.md`. Consumer customization guidance distinguishes this default from verified ASD-STE100 compliance. The smoke scenario, changelog, and distribution manifest were updated. The real `skills@latest` and Pi smoke test passes, as do all 56 tests and structural, release, installation, syntax, and link checks.
