# Starting a new project

v0.1 supports one configured consumer root per Git repository.

1. Select the workflows you want and install `configure-project` plus their complete [dependency closure](workflow-dependencies.md).
2. Preserve each selected skill directory intact and place it where the consumer's agent can discover it. No particular parent directory is required.
3. Invoke `configure-project` from the Git repository root before using another workflow.
4. Record the exact distribution source and release version or immutable commit SHA.
5. Accept or change the recommended issue backend and artifact capabilities.
6. Review the complete proposed `AGENTS.md`, `.agents/workflows.yaml`, and `docs/agents/` dry run. Nothing is written before approval.
7. [Verify the consumer installation](verifying-installation.md).
8. Commit the configuration and guidance before creating project artifacts.

`.agents/workflows.yaml` is the repository's single canonical workflow configuration. Monorepos may choose suitable artifact paths within it, but v0.1 does not support nested configurations or inheritance.

Directories for optional artifacts and local issues are created only when their first content is written.
