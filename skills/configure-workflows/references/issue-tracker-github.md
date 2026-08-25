# Issue tracker: GitHub

Issues live in GitHub Cloud. Use the generated `docs/agents/github-issues.py` helper from the repository root. The backend requires authenticated `gh`, enabled Issues, repository write permission, native sub-issues, and native issue dependencies. It does not fall back to task lists or body-text relationships.

Read `issue_tracker.login` from `.agents/workflows.yaml`, then pass it to every helper command:

```bash
helper=docs/agents/github-issues.py
login=CONFIGURED_GITHUB_LOGIN
python3 "$helper" --login "$login" preflight
```

The helper fails before repository access when the configured account is missing, invalid, or not the active `github.com` account. If another account is active, ask the user to run `gh auth switch --hostname github.com --user "$login"`, then rerun preflight. Never switch global authentication silently.

Every mutating operation still requires the approval boundary defined by the invoking workflow. Use a temporary file or quoted heredoc for multiline bodies. Never construct unsafe shell strings from issue content.

## Managed issue kinds

Every managed issue has exactly one semantic-kind label:

| Label | Meaning |
| --- | --- |
| `workflow:initiative` | Parent map for a bounded initiative |
| `workflow:bug` | Accepted defect with observable incorrect behavior |
| `workflow:implementation` | Executable vertical delivery slice |
| `workflow:clarification` | Question requiring a human decision |
| `workflow:research` | Focused external fact-finding question |
| `workflow:prototype` | Question answered through a disposable concrete artifact |
| `workflow:prerequisite` | Enabling action that does not implement the destination |

Do not duplicate state with labels. Open and closed state track lifecycle, assignees track claims, native dependencies track blocking, and close reasons distinguish resolution from cancellation.

## Label provisioning

Generate a deterministic plan, show it to the user, and apply that exact plan only after approval:

```bash
plan="$(mktemp)"
python3 "$helper" --login "$login" labels-plan --output "$plan"
python3 "$helper" --login "$login" labels-apply --plan-file "$plan" --yes
rm -f "$plan"
```

Application fails when repository label state changed after planning. Existing managed labels are updated only when the reviewed plan says so.

## Core operations

### Create

Create one bounded issue with a title, Markdown body, and semantic kind:

```bash
python3 "$helper" --login "$login" create --kind bug --title "..." --body-file /tmp/body.md
python3 "$helper" --login "$login" create --kind implementation --label team:platform --title "..." --body-file /tmp/body.md
```

A raw report does not automatically deserve an issue. Search first. Create one issue only for an accepted actionable defect or work outcome. Keep authoritative RFCs, ARPs, specifications, domain models, and technical baselines in repository documents and link them.

### Read

Retrieve the complete issue, comments, direct sub-issues, and blockers:

```bash
python3 "$helper" --login "$login" read 123
```

### List

List in stable issue-number order. Filters may select state, kind, assignee, or direct parent:

```bash
python3 "$helper" --login "$login" list --state all
python3 "$helper" --login "$login" list --kind bug --state open
python3 "$helper" --login "$login" list --label team:platform --state open
python3 "$helper" --login "$login" list --parent 100 --state open
python3 "$helper" --login "$login" list --assignee @me
```

The helper paginates complete REST collections. Use the returned JSON for duplicate and overlap searches; search by behavior and outcome, not only exact words.

### Update

Change title, body, semantic kind, ordinary labels, or reopen state while preserving the single workflow kind:

```bash
python3 "$helper" --login "$login" update 123 --title "..."
python3 "$helper" --login "$login" update 123 --body-file /tmp/body.md --kind implementation
python3 "$helper" --login "$login" update 123 --add-label team:platform --remove-label needs-triage
python3 "$helper" --login "$login" update 123 --state open
```

Use `--kind` for managed labels. The helper rejects attempts to add or remove `workflow:*` labels through the ordinary-label options.

### Comment

Append chronological discussion without rewriting the original question:

```bash
python3 "$helper" --login "$login" comment 123 --body-file /tmp/comment.md
```

### Claim

Claim before substantive work. The helper rejects an observed existing assignee:

```bash
python3 "$helper" --login "$login" claim 123
```

GitHub does not provide atomic compare-and-set assignment. Two truly simultaneous claims can still race; re-read the issue after claiming when concurrent work is likely.

### Resolve

Post a resolution comment and close with reason `completed`:

```bash
python3 "$helper" --login "$login" resolve 123 --body-file /tmp/resolution.md
```

### Cancel

Post the scope reason and close with reason `not planned`:

```bash
python3 "$helper" --login "$login" cancel 123 --body-file /tmp/cancellation.md
```

A cancelled blocker does not satisfy a dependency unless project policy explicitly says otherwise.

## Native relationships

### Parent

Add or remove a native parent-child relationship. Repeating the same operation is safe:

```bash
python3 "$helper" --login "$login" parent-add 100 123
python3 "$helper" --login "$login" parent-remove 100 123
```

The first number is the parent map and the second is the child. The helper never silently replaces another parent.

### Block

Add or remove a native dependency. Repeating the same operation is safe:

```bash
python3 "$helper" --login "$login" block-add 123 110
python3 "$helper" --login "$login" block-remove 123 110
```

The first issue is blocked; the second issue is the blocker. Relationship writes resolve issue numbers to GitHub's numeric database IDs.

### Frontier

Find direct children that are open, unassigned, and have only blockers closed as `completed`:

```bash
python3 "$helper" --login "$login" frontier 100
```

Results use ascending issue-number order. Closed `not planned` blockers do not make a child eligible.

## Initiative planning

- The parent map uses `workflow:initiative`.
- Clarification, research, prototype, and prerequisite tickets are native sub-issues with their corresponding kind.
- Approved delivery slices use `workflow:implementation`; accepted defects use `workflow:bug`.
- The map body is a concise index of destination, scope, decisions so far, unresolved fog, completion criteria, and authoritative links.
- Detailed answers and evidence live in child resolution comments. Append only a linked one-line gist to the map.
- Close the map only after initiative closure reconciles unresolved, blocked, cancelled, and deferred children.
