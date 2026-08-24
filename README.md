# Agent Workflows

A portable set of agent skills for turning ambiguity into durable project knowledge and executable work.

The kit separates:

- **skills**, which describe reusable workflows;
- **backend instructions**, which map issue operations to GitHub or committed Markdown;
- **project configuration**, which selects paths and optional capabilities; and
- **artifacts**, which remain owned by the project that creates them.

## Workflow

```text
clarify-intent ─┬─> model-domain
                ├─> develop-rfc ─> record-arp
                └─> plan-initiative

plan-initiative ─> author-specification ─> plan-implementation
```

Research, prototypes, questionnaires, meetings, and handoffs support this flow without becoming authoritative by themselves.

## Install

v0.2 vendors skills into each consumer repository. Start with `configure-project` and the workflows you explicitly want; the initial copy may omit transitive dependencies.

An Agent Skills-compatible installer may perform the copy. For example:

```bash
npx skills@latest add synthlike/agent-workflows
```

This command is illustrative; v0.2 does not guarantee a third-party installer's syntax, destination, or update behavior. An equivalent intact manual copy is supported at any repository-contained location the consumer's harness discovers.

From the consumer Git root, invoke `configure-project` before another workflow. Its installed lifecycle command reads the [release manifest](docs/release-manifest.md), calculates closure, and produces a complete dry run. When dependencies are missing, supply the matching release bundle, approve every source and destination, apply the non-destructive plan, and confirm harness discovery. Then approve schema-2 configuration and guidance, run [installed verification](docs/verifying-installation.md), and commit before creating artifacts.

See [Fresh-project configuration](docs/fresh-project-configuration.md) for commands and safety behavior.

## v0.2 contract

- [Current specification: fresh-project lifecycle](docs/specifications/v0.2-fresh-project-lifecycle.md)
- [Scope decision: ARP-0004](docs/decisions/ARP-0004-ship-v0.2-for-fresh-project-adoption.md)
- [Scope amendment: RFC-0003](docs/rfcs/RFC-0003-reduce-v0.2-to-fresh-project-lifecycle.md)
- [Release manifest and bundle](docs/release-manifest.md)
- [Workflow configuration schema 2](docs/workflow-configuration.md)
- [Installed verification](docs/verifying-installation.md)

The v0.1 [RFC](docs/rfcs/RFC-0001-v0.1-installation-and-consumer-project-contract.md), [ownership ARP](docs/decisions/ARP-0001-use-a-vendored-consumer-owned-installation-boundary.md), and [specification](docs/specifications/v0.1-installation-and-consumer-project-contract.md) remain historical context.

## Start here

- [Choosing a workflow](docs/choosing-a-workflow.md)
- [Artifact model](docs/artifact-model.md)
- [Workflow dependencies](docs/workflow-dependencies.md)
- [Release manifest and bundle](docs/release-manifest.md)
- [Workflow configuration schema 2](docs/workflow-configuration.md)
- [Verifying a consumer installation](docs/verifying-installation.md)
- [Issue-tracker backends](docs/issue-tracker-backends.md)
- [Starting a new project](docs/starting-a-new-project.md)
- [Fresh-project configuration](docs/fresh-project-configuration.md)
- [Adopting in an existing project](docs/adopting-in-existing-project.md)

## Status

Early development. The initial scope is planning, design knowledge, and work decomposition, not implementation or code-quality automation.

## Attribution

Several workflows are adapted from [`mattpocock/skills`](https://github.com/mattpocock/skills), commit `6654f6b60cd9d5be8b54c6fafe44346dabeb3b76`, under the MIT License. See [NOTICE](NOTICE).
