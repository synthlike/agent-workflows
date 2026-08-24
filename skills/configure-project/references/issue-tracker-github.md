# Issue tracker: GitHub

Issues live in GitHub Issues. Use `gh` from the repository root.

## Core operations

- Create: `gh issue create --title "..." --body-file <file>`.
- Read: `gh issue view <number> --comments`.
- List: `gh issue list --state open --json number,title,body,labels,assignees` with suitable filters.
- Update: `gh issue edit <number>`.
- Comment: `gh issue comment <number> --body-file <file>`.
- Claim: `gh issue edit <number> --add-assignee @me` before substantive work.
- Resolve: post a resolution comment, then `gh issue close <number>`.
- Cancel: post the scope reason, then close without indexing it as a decision.

Use a temporary file or quoted heredoc for multiline bodies. Never construct unsafe shell strings from untrusted issue content.

## Relationships

Use GitHub sub-issues for parent-child relationships where enabled. Otherwise put the child in a task list on the parent and add a `Part of #<parent>` line to the child.

Use native issue dependencies where available. GitHub's dependency API requires the blocker's numeric database `id`, not its issue number or GraphQL `node_id`. Otherwise use a `Blocked by: #N` body convention.

## Initiative planning

- Maps carry `initiative:map`.
- Children carry one of `initiative:research`, `initiative:prototype`, `initiative:clarification`, or `initiative:task`.
- An assignee represents a claim.
- The frontier contains open children with no assignee and no open blockers.
- Resolve a child with a resolution comment, close it, then append a linked one-line gist to the map.
