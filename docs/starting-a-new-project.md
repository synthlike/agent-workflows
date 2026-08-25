# Starting a new project

Agent Workflows supports one configured root per consumer workspace. Git is optional; a workspace may use Git, another version-control system, or no version control.

1. Use an Agent Skills-compatible installer or intact manual copy to install the complete Agent Workflows skill set, including `configure-workflows`. Preserve each skill directory intact and place it where the consumer's agent can discover it. No particular parent directory is required.
2. Invoke `configure-workflows` from the intended consumer workspace root before using another workflow. Let it detect version control; if none exists, confirm whether the workspace is intentionally unversioned.
3. Choose the workflows you intend to use. The schema records this explicit selection separately from the complete installed inventory.
4. Let the installed lifecycle command inspect the harness-discovered directories, require the complete distribution, and calculate the [dependency closure](workflow-dependencies.md).
5. Accept or change the recommended issue backend and artifact capabilities. When selecting GitHub, choose an authenticated account explicitly, then review its capability preflight and complete managed-label plan.
6. Review the complete proposed schema-2 `.agents/workflows.yaml`, `AGENTS.md`, and `docs/agents/` dry run. Nothing is written before approval.
7. [Verify the consumer installation](verifying-installation.md).
8. When the workspace uses version control, commit or otherwise land the installed skill directories, configuration, and guidance before creating project artifacts. In an intentionally unversioned workspace, acknowledge that no such history checkpoint exists.
9. When a founder has an early product idea, invoke `frame-product-problem` before treating it as requirements. Approve a project-owned discovery location, challenge the problem and audience, and plan non-leading customer validation.
10. When the principal application stack is already selected, invoke `establish-technical-baseline` before product-dependent architecture work. Approve a project-owned documentation location and keep unknown product questions deferred.

If inspection reports an incomplete or modified distribution, stop configuration and correct the installation through the external installer or a reviewed intact manual copy. `configure-workflows` does not write skill directories. See [Fresh-project configuration](fresh-project-configuration.md).

`.agents/workflows.yaml` is the workspace's single canonical workflow configuration. It records immutable distribution identity, user-selected workflows, and every harness-discovered skill path. Large or multi-package workspaces may choose suitable consumer-root-contained paths, but nested configurations and inheritance are not supported.

Directories for optional artifacts and local issues are created only when their first content is written.
