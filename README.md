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

Install the skills using an Agent Skills-compatible installer, for example:

```bash
npx skills@latest add <owner>/agent-workflows
```

Select `configure-project` and the workflows you want. Then invoke `configure-project` once in the target repository. It inspects existing conventions, asks only about unresolved choices, and writes `.agents/workflows.yaml` plus concise agent documentation.

Until this repository is published, point your agent at `skills/` directly or copy selected skill directories into a supported project skill location such as `.agents/skills/`.

## Start here

- [Choosing a workflow](docs/choosing-a-workflow.md)
- [Artifact model](docs/artifact-model.md)
- [Issue-tracker backends](docs/issue-tracker-backends.md)
- [Starting a new project](docs/starting-a-new-project.md)
- [Adopting in an existing project](docs/adopting-in-existing-project.md)

## Status

Early development. The initial scope is planning, design knowledge, and work decomposition, not implementation or code-quality automation.

## Attribution

Several workflows are adapted from [`mattpocock/skills`](https://github.com/mattpocock/skills), commit `6654f6b60cd9d5be8b54c6fafe44346dabeb3b76`, under the MIT License. See [NOTICE](NOTICE).
