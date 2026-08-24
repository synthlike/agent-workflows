# Issue tracker: Local Markdown

Issues are committed Markdown files under the configured root, normally `.project/`.

## Layout

```text
.project/
├── issues/
│   └── ISSUE-0001-example.md
└── efforts/
    └── example/
        ├── map.md
        └── issues/
            └── 01-answer-a-question.md
```

General issues use repository-wide IDs. Decision tickets inside an effort may use effort-local numbers because their path is their stable identity.

## Issue format

```md
---
id: ISSUE-0001
title: Example
kind: task
status: open
created: 2026-01-01
assignee:
parent:
blocked_by: []
labels: []
---

# Example

## Question or work

...

## Comments

## Resolution
```

Statuses are `open`, `claimed`, `resolved`, or `cancelled`. Blocking is derived from `blocked_by`; do not duplicate it as a status.

## Core operations

- Create a uniquely named Markdown file with complete frontmatter.
- Read the complete referenced file.
- List or filter by scanning frontmatter.
- Update title, body, state, labels, and relationships by editing the file.
- Append discussion under `## Comments` with a date and author.
- Claim by setting `status: claimed` and `assignee` before substantive work.
- Resolve by writing `## Resolution`, setting `status: resolved`, and saving the file.
- Cancel by recording the scope reason and setting `status: cancelled`.
- Represent parents and blockers with relative file links in `parent` and `blocked_by`.

## Frontier

Scan an effort's issue directory in filename order. A frontier issue:

- has `status: open`;
- has no assignee; and
- has only `resolved` blockers.

Local claims are not atomic across unsynchronized clones or branches. Synchronize before claiming concurrent work.
