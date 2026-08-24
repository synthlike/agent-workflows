# Adopting in an existing project

Install intact copies of the complete Agent Workflows skill set, then run `configure-project` from the Git repository root. Review existing skill names and destinations first; never replace a project-owned skill directory. Schema 2 records explicitly selected workflows separately from the complete installed inventory. Let the skill inspect existing conventions before proposing changes and explicitly approve the configuration dry run before it writes anything.

If the complete distribution cannot be installed without conflicting with an existing skill, stop adoption and resolve ownership or naming outside `configure-project`. The workflow reports installation problems but never creates, replaces, or removes skill directories.

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
