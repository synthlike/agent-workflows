---
name: capture-meeting
description: Capture concise meeting minutes and identify decisions, requirements, actions, and open questions for promotion to canonical artifacts. Use only when meeting records are wanted.
disable-model-invocation: true
license: MIT
---

# Capture Meeting

Meeting notes are optional historical evidence. They are not the canonical source of technical decisions, requirements, or work.

Read `.agents/workflows.yaml`. If meeting notes are disabled, ask before enabling or writing them. Use the configured path and [meeting template](references/meeting-template.md).

## Capture

- Record purpose, participants when appropriate, and concise discussion notes.
- Separate observed decisions, new or changed requirements, actions, and open questions.
- Attribute owners and due dates only when stated.
- Mark uncertainty; do not infer consensus from silence.
- Avoid unnecessary personal or sensitive information.

## Promote

After drafting, ask which extracted items should become authoritative:

- technical ambiguity -> RFC;
- consequential accepted technical decision -> ARP;
- agreed behavior or requirement -> specification;
- action or implementation slice -> issue; and
- resolved terminology -> domain model.

Create promoted artifacts only after confirmation, then link them from the minutes. A fact appearing only in meeting notes remains non-authoritative.
