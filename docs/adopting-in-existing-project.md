# Adopting in an existing project

Install an intact, dependency-closed workflow selection, then run `configure-project` from the Git repository root. Let it inspect existing conventions before proposing changes. Review and explicitly approve the complete dry run before it writes anything.

Prefer adoption over migration:

- Reuse an existing ADR or decision directory unless a rename has clear value.
- Reuse existing RFC, specification, and issue conventions.
- Preserve a root `CONTEXT.md` or existing context map.
- Add a concise pointer to the existing `AGENTS.md` or equivalent; never replace it.
- Keep meeting notes disabled unless the project wants them.
- Record the exact installed distribution source and release version or immutable commit SHA.
- Keep one `.agents/workflows.yaml` at the Git root; do not introduce nested configurations.

## Ownership during adoption

The installed, unmodified skill directories are distribution-managed reusable files. The consumer owns `.agents/workflows.yaml`, root agent guidance, `docs/agents/`, issue-backend state, all project artifacts, and any explicit local skill modifications. Installation and setup must preserve consumer-owned files.

Migration or renaming of existing artifacts is separate, explicitly approved work and must not happen as a side effect of installation or configuration. Optional artifact and local-issue directories remain absent until their first content is written.

Finish by [verifying the consumer installation](verifying-installation.md) and committing the reviewed setup.
