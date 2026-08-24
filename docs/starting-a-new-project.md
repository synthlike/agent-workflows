# Starting a new project

Agent Workflows supports one configured consumer root per Git repository.

1. Use an Agent Skills-compatible installer or intact manual copy to install the complete Agent Workflows skill set, including `configure-project`. Preserve each skill directory intact and place it where the consumer's agent can discover it. No particular parent directory is required.
2. Invoke `configure-project` from the Git repository root before using another workflow.
3. Choose the workflows you intend to use. The schema records this explicit selection separately from the complete installed inventory.
4. Let the installed lifecycle command inspect the harness-discovered directories and calculate the [dependency closure](workflow-dependencies.md). A complete installation needs no release bundle during normal setup.
5. Accept or change the recommended issue backend and artifact capabilities.
6. Review the complete proposed schema-2 `.agents/workflows.yaml`, `AGENTS.md`, and `docs/agents/` dry run. Nothing is written before approval.
7. [Verify the consumer installation](verifying-installation.md).
8. Commit the installed skill directories, configuration, and guidance before creating project artifacts.
9. When a founder has an early product idea, invoke `frame-product-problem` before treating it as requirements. Approve a project-owned discovery location, challenge the problem and audience, and plan non-leading customer validation.
10. When the principal application stack is already selected, invoke `establish-technical-baseline` before product-dependent architecture work. Approve a project-owned documentation location and keep unknown product questions deferred.

Selective installation remains supported. When installed workflows omit required dependencies, supply the matching verified release bundle, review every proposed source and destination, and approve the non-destructive missing-skill plan. See [Fresh-project configuration](fresh-project-configuration.md).

`.agents/workflows.yaml` is the repository's single canonical workflow configuration. It records immutable distribution identity, user-selected workflows, and every harness-discovered skill path. Monorepos may choose suitable repository-contained paths, but nested configurations and inheritance are not supported.

Directories for optional artifacts and local issues are created only when their first content is written.
