# Adopting in an existing project

Install intact copies of `configure-project` and the workflows you explicitly select, then run `configure-project` from the Git repository root. The installed lifecycle command calculates closure and may propose adding missing dependencies from the verified current-release bundle. Let the skill inspect existing conventions before proposing changes. Review and explicitly approve every skill destination and the complete schema-2 configuration dry run before it writes anything.

Prefer adoption over migration:

- Reuse an existing ADR or decision directory unless a rename has clear value.
- Reuse existing RFC, specification, and issue conventions.
- Preserve a root `CONTEXT.md` or existing context map.
- Add a concise pointer to the existing `AGENTS.md` or equivalent; never replace it.
- Keep meeting notes disabled unless the project wants them.
- Record the exact installed distribution source and release version or immutable commit SHA.
- Record explicitly selected workflows separately from transitive dependencies and map every harness-discovered skill path.
- Confirm harness discovery of the complete closure before final configuration.
- Keep one schema-2 `.agents/workflows.yaml` at the Git root; do not introduce nested configurations.

## Ownership during adoption

The installed, unmodified skill directories are distribution-managed reusable files. The consumer owns `.agents/workflows.yaml`, root agent guidance, `docs/agents/`, issue-backend state, all project artifacts, and any explicit local skill modifications. Installation and setup must preserve consumer-owned files.

Migration or renaming of existing artifacts is separate, explicitly approved work and must not happen as a side effect of installation or configuration. Optional artifact and local-issue directories remain absent until their first content is written.

Finish with [installed verification](verifying-installation.md), without a source checkout, and commit the reviewed setup.
