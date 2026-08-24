# Agent Workflows

A portable set of agent skills for turning ambiguity into durable project knowledge and executable work.

The kit separates:

- **skills**, which describe reusable workflows;
- **backend instructions**, which map issue operations to GitHub or committed Markdown;
- **project configuration**, which selects paths and optional capabilities; and
- **artifacts**, which remain owned by the project that creates them.

## Workflow

```text
frame-product-problem ─> prepare-questionnaire / research-question / prototype-design
                      └> plan-initiative

establish-technical-baseline

clarify-intent ─┬─> model-domain
                ├─> develop-rfc ─> record-arp
                └─> plan-initiative

plan-initiative ─> author-specification ─> plan-implementation

triage-issue ─> investigate-failure ─> capture-regression
                                      └> implementation ─> review-implementation
                                                              └> close-initiative
```

Research, prototypes, questionnaires, meetings, investigations, reviews, baselines, and handoffs support authoritative artifacts without replacing them.

## Install

v0.3 vendors skills into each consumer repository. Start with `configure-project` and the workflows you explicitly want; the initial copy may omit transitive dependencies.

An Agent Skills-compatible installer may perform the copy. For example:

```bash
npx skills@latest add synthlike/agent-workflows
```

This command is illustrative; v0.3 does not guarantee a third-party installer's syntax, destination, or update behavior. An equivalent intact manual copy is supported at any repository-contained location the consumer's harness discovers.

From the consumer Git root, invoke `configure-project` before another workflow. Its installed lifecycle command reads the [release manifest](docs/release-manifest.md), calculates closure, and produces a complete dry run. When dependencies are missing, supply the matching release bundle, approve every source and destination, apply the non-destructive plan, and confirm harness discovery. Then approve schema-2 configuration and guidance, run [installed verification](docs/verifying-installation.md), and commit before creating artifacts.

See [Fresh-project configuration](docs/fresh-project-configuration.md) for commands and safety behavior.

## v0.3 contract

- [Current specification: project-foundation and feedback workflows](docs/specifications/v0.3-project-foundation-and-feedback-workflows.md)
- [Scope decision: ARP-0005](docs/decisions/ARP-0005-focus-v0.3-on-project-feedback-workflows.md) and [product-framing refinement: ARP-0006](docs/decisions/ARP-0006-add-product-problem-framing-to-v0.3.md)
- [Scope RFC: RFC-0004](docs/rfcs/RFC-0004-focus-v0.3-on-project-feedback-workflows.md) and [product-framing amendment: RFC-0005](docs/rfcs/RFC-0005-add-product-problem-framing-to-v0.3.md)
- [v0.2 fresh-project lifecycle foundation](docs/specifications/v0.2-fresh-project-lifecycle.md), with its [scope RFC](docs/rfcs/RFC-0003-reduce-v0.2-to-fresh-project-lifecycle.md) and [decision](docs/decisions/ARP-0004-ship-v0.2-for-fresh-project-adoption.md)
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

Active early development. v0.3 covers product-problem framing, project foundations, planning and design knowledge, defect evidence, implementation conformance review, and initiative closure. It does not implement application code or automated cross-version maintenance.

## Attribution

Several workflows are adapted from [`mattpocock/skills`](https://github.com/mattpocock/skills), commit `6654f6b60cd9d5be8b54c6fafe44346dabeb3b76`, under the MIT License. See [NOTICE](NOTICE).
