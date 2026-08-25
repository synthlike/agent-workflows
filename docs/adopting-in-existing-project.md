# Adopting in an existing project

Install intact copies of the complete Agent Workflows skill set, then run `configure-workflows` from the intended consumer workspace root. Git is optional. Let the workflow detect version control, and confirm whether the workspace is intentionally unversioned when none is found. Review existing skill names and destinations first; never replace a project-owned skill directory. Schema 2 records explicitly selected workflows separately from the complete installed inventory. Let the skill inspect existing conventions before proposing changes and explicitly approve the configuration dry run before it writes anything.

If the complete distribution cannot be installed without conflicting with an existing skill, stop adoption and resolve ownership or naming outside `configure-workflows`. The workflow reports installation problems but never creates, replaces, or removes skill directories.

Prefer adoption over migration:

- Reuse an existing ADR or decision directory unless a rename has clear value.
- Reuse existing RFC, specification, and issue conventions.
- Preserve a root `CONTEXT.md` or existing context map.
- Add a concise pointer to the existing `AGENTS.md` or equivalent; never replace it.
- Ask what kind of project this is and how people and agents collaborate, then review each supporting-artifact retention recommendation.
- Keep meeting notes, retained prototypes, and durable handoffs disabled unless the project wants them.
- Enable research, questionnaires, and technical baselines by default, while preserving existing locations and retention policies.
- Record the exact installed distribution source and release version or immutable commit SHA.
- Record explicitly selected workflows separately from transitive dependencies and map every harness-discovered skill path.
- Confirm harness discovery of the complete closure before final configuration.
- Keep one `.agents/workflows.yaml` at the consumer workspace root; do not introduce nested configurations.

## Ownership during adoption

The installed, unmodified skill directories are distribution-managed reusable files. The consumer owns `.agents/workflows.yaml`, root agent guidance, `docs/agents/`, issue-backend state, all project artifacts, and any explicit local skill modifications. Installation and setup must preserve consumer-owned files.

Migration or renaming of existing artifacts is separate, explicitly approved work and must not happen as a side effect of installation or configuration. Optional artifact and local-issue directories remain absent until their first content is written.

Finish with [installed verification](verifying-installation.md), without a source checkout. When version control is present, commit or otherwise land the reviewed setup; an intentionally unversioned workspace has no equivalent history checkpoint.
