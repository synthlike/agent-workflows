# Issue-tracker backends

Workflow skills use semantic issue operations. The configured backend determines how those operations are performed.

Supported backends:

- **GitHub:** GitHub Issues through `gh`, with native sub-issues and dependencies where available.
- **Local Markdown:** committed files under a configurable project directory, normally `.project/`.

`configure-project` writes the selected instructions to `docs/agents/issue-tracker.md`. Other skills must read that document before operating on issues.

See the [backend contract](../backends/issue-tracker/contract.md) and concrete [GitHub](../backends/issue-tracker/github.md) and [local Markdown](../backends/issue-tracker/local-markdown.md) adapters.

## Backend limitations

Local Markdown cannot provide atomic claims across unsynchronized clones or branches. It is appropriate for a single working tree or a team that synchronizes before claiming work. GitHub is preferable for highly concurrent planning.
