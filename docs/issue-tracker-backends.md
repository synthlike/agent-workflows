# Issue-tracker backends

Workflow skills use semantic issue operations. The configured backend determines how those operations are performed.

Supported backends:

- **GitHub:** GitHub Cloud through an executable `gh`-based helper, requiring native sub-issues and dependencies.
- **Local Markdown:** committed files under a configurable project directory, normally `.project/`.

`configure-workflows` writes the selected instructions to `docs/agents/issue-tracker.md`. Other skills must read that document before operating on issues.

See the [backend contract](../backends/issue-tracker/contract.md) and concrete [GitHub](../backends/issue-tracker/github.md) and [local Markdown](../backends/issue-tracker/local-markdown.md) adapters.

## GitHub model

GitHub configuration records the intended authenticated login. Configuration shows all authenticated account names and asks which one to use; it does not assume that the active account is intended or switch accounts silently. Every helper command fails before repository access unless that configured login is authenticated and active.

GitHub initiatives are parent map issues with native sub-issues and dependencies. Managed issues have exactly one `workflow:*` semantic-kind label. Assignees represent claims, `completed` represents resolution, and `not planned` represents cancellation. `configure-workflows` runs a read-only preflight and shows a stale-safe label plan before any repository mutation.

GitHub issues hold bounded work, planning history, investigation evidence, reviews, and closure summaries. Authoritative RFCs, ARPs, specifications, domain models, and technical baselines remain repository documents and are linked from issues.

## Backend limitations

Local Markdown cannot provide atomic claims across unsynchronized clones or branches. It is appropriate for a single working tree or a team that synchronizes before claiming work. GitHub assignment also lacks compare-and-set semantics, so two simultaneous claims can race even though the helper rejects an observed existing assignee. The GitHub backend currently targets GitHub Cloud because native sub-issues are not documented for GitHub Enterprise Server.
