# Adopting in an existing project

Run `configure-project` and let it inspect existing conventions before writing anything.

Prefer adoption over migration:

- Reuse an existing ADR or decision directory unless a rename has clear value.
- Reuse existing RFC, specification, and issue conventions.
- Preserve a root `CONTEXT.md` or existing context map.
- Add a concise pointer to the existing `AGENTS.md` or equivalent; never replace it.
- Keep meeting notes disabled unless the project wants them.

The setup workflow must present a dry run. Migration of existing artifacts is separate, explicit work and must not happen as a side effect of installation.
