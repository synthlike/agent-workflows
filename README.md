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

v0.1 vendors skills into each consumer repository. Choose the workflows you want, then use the [dependency table](docs/workflow-dependencies.md) to include `configure-project` and their complete transitive closure.

An Agent Skills-compatible installer may perform the copy. For example:

```bash
npx skills@latest add synthlike/agent-workflows
```

This command is illustrative; v0.1 does not guarantee a third-party installer's syntax, selection behavior, destination, or update behavior. An equivalent manual copy is supported when every selected skill directory remains intact and the consumer's agent can discover it. The harness may use any discoverable parent location; `.agents/skills/` is only one example.

From the consumer's Git root, invoke `configure-project` before any other installed workflow. Approve its complete dry run and record the exact distribution source plus release version or immutable commit SHA in the single root `.agents/workflows.yaml`. Then [verify the consumer installation](docs/verifying-installation.md) and commit the reviewed configuration and guidance before creating artifacts.


## v0.1 contract

- [Specification: installation and consumer-project contract](docs/specifications/v0.1-installation-and-consumer-project-contract.md)
- [ARP-0001: accepted installation and ownership boundary](docs/decisions/ARP-0001-use-a-vendored-consumer-owned-installation-boundary.md)
- [RFC-0001: design discussion and resolution](docs/rfcs/RFC-0001-v0.1-installation-and-consumer-project-contract.md)
- [Workflow dependency table](docs/workflow-dependencies.md)
- [Consumer verification](docs/verifying-installation.md)

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
