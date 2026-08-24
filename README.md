# Agent Workflows

Reusable workflows that help AI coding agents turn uncertain ideas, technical questions, and reported problems into reviewed project knowledge and executable work.

Use Agent Workflows to:

- interview a founder and test a product-problem hypothesis;
- establish a minimal technical baseline;
- clarify requirements before implementation;
- investigate failures without silently changing code;
- plan initiatives and implementation issues;
- review completed work against agreed specifications; and
- close initiatives using evidence rather than issue status alone.

The workflows do not implement application code. They structure the evidence, decisions, specifications, and plans around implementation.

## Choose a starting workflow

| If you want to… | Start with |
| --- | --- |
| Examine a founder's product idea | `frame-product-problem` |
| Establish technical foundations | `establish-technical-baseline` |
| Clarify an ambiguous requirement | `clarify-intent` |
| Resolve a design disagreement | `develop-rfc` |
| Plan a body of work | `plan-initiative` |
| Triage a reported problem | `triage-issue` |
| Diagnose a reproducible failure | `investigate-failure` |
| Review completed implementation | `review-implementation` |
| Determine whether an initiative succeeded | `close-initiative` |

See [Choosing a workflow](docs/choosing-a-workflow.md) for the complete guide and [Workflow dependencies](docs/workflow-dependencies.md) for the full workflow graph.

## Quick start

Agent Workflows copies skills into each consumer repository, where they remain owned and versioned by that project. The recommended setup installs the complete workflow set; it is small, avoids dependency downloads during configuration, and leaves you free to select only the workflows you intend to use.

For example, an Agent Skills-compatible installer can copy all skills:

```bash
npx skills@latest add synthlike/agent-workflows \
  --skill '*' \
  --copy
```

The installer can ask which agent harness should discover them. Installer syntax, destinations, and update behavior vary. An intact manual copy also works at any repository-contained location your agent harness discovers.

From the consumer repository root, tell your agent:

> Use `configure-project` to configure this fresh repository. Select `frame-product-problem` as my initial workflow, inventory every installed skill, show me the complete dry run, and ask before writing anything.

`configure-project` inspects the repository, records explicit workflow intent separately from the complete installed inventory, and checks dependency closure. It then guides you through project configuration, installed verification, and the first commit. It does not create, replace, or remove skill directories and does not silently modify consumer-owned content.

Read [Fresh-project configuration](docs/fresh-project-configuration.md) for the complete procedure and safety behavior. For a repository that already has conventions or artifacts, use [Adopting in an existing project](docs/adopting-in-existing-project.md) instead.

## Example: start with a founder's idea

A typical product-discovery route is:

```text
configure-project
  -> frame-product-problem
  -> prepare-questionnaire
  -> capture-meeting
  -> reassess the problem
  -> plan-initiative
```

After configuration, tell your agent:

> Use `frame-product-problem` to interview me about my product idea. Ask exactly one question at a time, distinguish founder beliefs from evidence, challenge counter-hypotheses, and do not assume that my proposed solution is the real problem.

The workflow helps separate the proposed solution from the observed problem, identify actors and current alternatives, classify claims by evidence, and plan non-leading customer validation. It does not call an idea “validated” without real customer or behavioral evidence. The founder remains responsible for deciding whether to continue, narrow, reframe, pivot, or stop.

## How the kit is organized

- **Skills** describe reusable semantic workflows.
- **Backend instructions** map issue operations to GitHub or committed Markdown.
- **Project configuration** records selected workflows, installed skill paths, and optional artifact locations.
- **Artifacts** remain owned by the project that creates them.

Research, prototypes, questionnaires, meetings, investigations, reviews, baselines, and handoffs support authoritative specifications and decisions without replacing them. Read [Artifact model](docs/artifact-model.md) for the authority boundaries.

## Current guarantees

- Skills are vendored into a consumer-owned repository boundary.
- Schema 2 records immutable distribution identity, selected workflows, and exact installed paths.
- Fresh setup calculates dependency closure before writing.
- Installation plans are explicit, reviewed, and non-destructive.
- Installed verification works without the Agent Workflows source checkout.
- Issue operations follow the configured [issue-tracker backend](docs/issue-tracker-backends.md).
- Projects choose and own artifact paths; optional directories are created only when needed.

The current workflow behavior is defined by the [project-foundation and feedback specification](docs/specifications/v0.3-project-foundation-and-feedback-workflows.md). Distribution behavior is documented in [Distribution manifest](docs/distribution-manifest.md), [Workflow configuration schema 2](docs/workflow-configuration.md), and [Verifying a consumer installation](docs/verifying-installation.md).

## Documentation

### Getting started

- [Starting a new project](docs/starting-a-new-project.md)
- [Fresh-project configuration](docs/fresh-project-configuration.md)
- [Adopting in an existing project](docs/adopting-in-existing-project.md)
- [Choosing a workflow](docs/choosing-a-workflow.md)

### Operating and customizing

- [Artifact model](docs/artifact-model.md)
- [Workflow dependencies](docs/workflow-dependencies.md)
- [Issue-tracker backends](docs/issue-tracker-backends.md)
- [Distribution manifest](docs/distribution-manifest.md)
- [Workflow configuration schema 2](docs/workflow-configuration.md)
- [Verifying a consumer installation](docs/verifying-installation.md)
- [Customizing a project](docs/customizing.md)
- [Updating vendored workflows](docs/updating.md)

## Design history

The current product-foundation and feedback scope was established by [RFC-0004](docs/rfcs/RFC-0004-focus-v0.3-on-project-feedback-workflows.md), [ARP-0005](docs/decisions/ARP-0005-focus-v0.3-on-project-feedback-workflows.md), and the product-framing refinement in [RFC-0005](docs/rfcs/RFC-0005-add-product-problem-framing-to-v0.3.md) and [ARP-0006](docs/decisions/ARP-0006-add-product-problem-framing-to-v0.3.md).

The fresh-project lifecycle foundation is recorded in the [v0.2 specification](docs/specifications/v0.2-fresh-project-lifecycle.md), [RFC-0003](docs/rfcs/RFC-0003-reduce-v0.2-to-fresh-project-lifecycle.md), and [ARP-0004](docs/decisions/ARP-0004-ship-v0.2-for-fresh-project-adoption.md). The v0.1 [RFC](docs/rfcs/RFC-0001-v0.1-installation-and-consumer-project-contract.md), [ownership decision](docs/decisions/ARP-0001-use-a-vendored-consumer-owned-installation-boundary.md), and [specification](docs/specifications/v0.1-installation-and-consumer-project-contract.md) remain historical context.

## Status

Active early development. The current workflow set covers product-problem framing, project foundations, planning and design knowledge, defect evidence, implementation conformance review, and initiative closure. It does not implement application code or automated cross-version maintenance.

## Attribution

Several workflows are adapted from [`mattpocock/skills`](https://github.com/mattpocock/skills), commit `6654f6b60cd9d5be8b54c6fafe44346dabeb3b76`, under the MIT License. See [NOTICE](NOTICE).
