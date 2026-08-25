# GitHub native issue relationships

## Question

Which official GitHub capabilities and identifiers are required for a deterministic issue backend with initiative sub-issues, blockers, and distinguishable closure outcomes?

## Verified facts

- GitHub provides REST endpoints to list, add, remove, and reprioritize sub-issues. Adding and removing use the sub-issue's numeric database `id`, not its issue number or GraphQL node ID. The official endpoint documentation lists GitHub Free, Pro, Team, and Enterprise Cloud, but not GitHub Enterprise Server. [Sub-issues endpoints](https://docs.github.com/en/rest/issues/sub-issues)
- GitHub provides REST endpoints to list issues that block another issue, add a blocking issue, remove it, and list issues blocked by an issue. Adding and removing use the blocker's numeric database `id`. The documentation lists GitHub Enterprise Server 3.19 or later as well as GitHub Cloud. [Issue dependency endpoints](https://docs.github.com/en/rest/issues/issue-dependencies)
- Updating an issue supports `state_reason` values `completed`, `not_planned`, and `reopened`, allowing resolved and cancelled work to remain machine-distinguishable. [Issues endpoints](https://docs.github.com/en/rest/issues/issues#update-an-issue)
- `gh api` supports placeholder expansion from the current repository, typed request fields, pagination, and slurping paginated responses into an outer JSON array. [GitHub CLI `gh api` manual](https://cli.github.com/manual/gh_api)
- `gh auth status` reports every known account and identifies the active account used for a host. Its JSON output can list account identity and state without requesting tokens. `gh auth switch --hostname HOST --user LOGIN` changes the active account globally for that host. [GitHub CLI `gh auth status` manual](https://cli.github.com/manual/gh_auth_status) and [`gh auth switch` manual](https://cli.github.com/manual/gh_auth_switch)

## Interpretation

A backend that requires both native sub-issues and dependencies should currently restrict itself to GitHub Cloud. Configuration should record an explicit account login and verify it before every operation, because `gh` may have several accounts and otherwise uses whichever account is active for the host. It should resolve issue numbers to numeric database IDs before relationship writes, paginate every relationship read, and derive a frontier from direct open children, assignment, and blocker closure reason. Native issue state and relationships should replace duplicated state labels.

## Remaining uncertainty

GitHub does not expose an atomic compare-and-set operation for assigning an unclaimed issue. The helper can reject an observed conflicting assignee, but simultaneous claims can still race.
