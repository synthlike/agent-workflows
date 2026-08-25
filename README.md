# Agent Workflows

Reusable workflows that help AI coding agents turn uncertain ideas, open questions, and reported problems into clear decisions and executable work.

Use them to discover what is worth building, clarify requirements, make technical decisions, plan implementation, investigate failures, and verify outcomes. The workflows guide the work around implementation; they do not replace the implementation itself.

## What you can do

### Discover and clarify

- Challenge a product idea and turn it into a testable problem hypothesis with `frame-product-problem`.
- Resolve unclear requirements or decisions through a focused interview with `clarify-intent`.
- Research an external question using primary sources with `research-question`.
- Create a lightweight prototype when discussion needs something concrete with `prototype-design`.
- Prepare stakeholder questions with `prepare-questionnaire` and capture the resulting discussion with `capture-meeting`.
- Establish shared terminology and domain boundaries with `model-domain`.

### Design and plan

- Set production-compatible engineering foundations for a chosen stack with `establish-technical-baseline`.
- Explore design alternatives with `develop-rfc` and record accepted technical decisions with `record-arp`.
- Turn agreed behavior into a specification with `author-specification`.
- Map a large, uncertain effort with `plan-initiative`.
- Break approved work into executable vertical slices with `plan-implementation`.

### Investigate and verify

- Turn an incoming report into a clear next step with `triage-issue`.
- Reproduce a failure and test possible causes with `investigate-failure`.
- Preserve a confirmed defect as a focused failing check with `capture-regression`.
- Review completed work against its agreed requirements with `review-implementation`.
- Close an initiative based on delivered evidence with `close-initiative`.

### Keep work moving

- Prepare concise context for another agent or session with `prepare-handoff`.
- Adapt the workflow kit to a new or existing repository with `configure-project`.

## Common workflows

You can use one skill on its own or combine skills into a longer workflow.

**Explore a product idea**

```text
frame-product-problem -> prepare-questionnaire -> capture-meeting
                      -> research-question / prototype-design
                      -> plan-initiative
```

**Plan a small, understood change**

```text
clarify-intent -> author-specification -> plan-implementation
```

**Resolve an ambiguous design**

```text
clarify-intent -> develop-rfc -> record-arp -> author-specification
```

**Plan a large, uncertain initiative**

```text
plan-initiative -> author-specification -> plan-implementation
```

**Diagnose a defect and protect the fix**

```text
triage-issue -> investigate-failure -> capture-regression
             -> implementation -> review-implementation
```

**Verify an initiative's outcome**

```text
review-implementation -> close-initiative
```

See [Choosing a workflow](docs/choosing-a-workflow.md) for more situations and combinations.

## Get started

Install the complete workflow set into your repository. For example, with an Agent Skills-compatible installer:

```bash
npx skills@latest add synthlike/agent-workflows \
  --skill '*' \
  --copy
```

Then, from your repository root, ask your agent to configure the kit:

> Use `configure-project` to configure this repository. Show me the complete dry run and ask before writing anything.

Once configured, ask for a workflow by name. For example:

> Use `clarify-intent` to help me work through this feature request.

> Use `investigate-failure` to diagnose this bug without changing production code.

> Use `plan-initiative` to map the decisions needed before we can build this.

For more help, read:

- [Starting a new project](docs/starting-a-new-project.md)
- [Fresh-project configuration](docs/fresh-project-configuration.md)
- [Adopting the workflows in an existing project](docs/adopting-in-existing-project.md)
- [Choosing a workflow](docs/choosing-a-workflow.md)
- [Customizing the workflows](docs/customizing.md)

## Reference

For operational details, see the [artifact model](docs/artifact-model.md), [workflow dependencies](docs/workflow-dependencies.md), and [issue-tracker options](docs/issue-tracker-backends.md). Installation details are covered by the [distribution manifest](docs/distribution-manifest.md), [configuration format](docs/workflow-configuration.md), and [installation verification guide](docs/verifying-installation.md).

## Status

Agent Workflows is in active early development. Projects keep and version their own installed copy of the workflows and any artifacts they create.

## Attribution

Several workflows are adapted from [`mattpocock/skills`](https://github.com/mattpocock/skills), commit `6654f6b60cd9d5be8b54c6fafe44346dabeb3b76`, under the MIT License. See [NOTICE](NOTICE).
