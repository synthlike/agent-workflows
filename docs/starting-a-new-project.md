# Starting a new project

v0.3 supports one configured consumer root per Git repository.

1. Select the workflows you want and install them with `configure-project`. The initial selection may omit transitive dependencies.
2. Preserve each installed skill directory intact and place it where the consumer's agent can discover it. No particular parent directory is required.
3. Invoke `configure-project` from the Git repository root before using another workflow.
4. Let the installed lifecycle command inspect the harness-discovered directories and calculate the [dependency closure](workflow-dependencies.md).
5. When dependencies are missing, supply the matching verified release bundle and review every proposed source and destination. See [Fresh-project configuration](fresh-project-configuration.md).
6. Approve the non-destructive missing-skill plan, apply it, and ask the harness to confirm discovery of the complete closure.
7. Accept or change the recommended issue backend and artifact capabilities.
8. Review the complete proposed schema-2 `.agents/workflows.yaml`, `AGENTS.md`, and `docs/agents/` dry run. Nothing is written before approval.
9. [Verify the consumer installation](verifying-installation.md).
10. Commit the installed skill directories, configuration, and guidance before creating project artifacts.
11. When a founder has an early product idea, invoke `frame-product-problem` before treating it as requirements. Approve a project-owned discovery location, challenge the problem and audience, and plan non-leading customer validation.
12. When the principal application stack is already selected, invoke `establish-technical-baseline` before product-dependent architecture work. Approve a project-owned documentation location and keep unknown product questions deferred.

`.agents/workflows.yaml` is the repository's single canonical workflow configuration. It records immutable distribution identity, user-selected workflows, and every harness-discovered skill path. Monorepos may choose suitable repository-contained paths, but v0.3 does not support nested configurations or inheritance.

Directories for optional artifacts and local issues are created only when their first content is written.
