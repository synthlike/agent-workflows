---
name: prepare-handoff
description: Prepare a compact handoff so another agent or session can continue work without duplicating durable artifacts. Use when work will continue in a fresh context.
disable-model-invocation: true
license: MIT
---

# Prepare Handoff

Write a temporary handoff tailored to the next session's purpose.

Include:

- the intended next outcome;
- current state and what changed in this session;
- unresolved questions and immediate next actions;
- relevant paths, issue links, branches, and commands;
- verification already performed; and
- suggested skills for the next session.

Do not duplicate specifications, RFCs, ARPs, maps, issues, commits, or diffs. Link them. Redact credentials, secrets, and unnecessary personal information.

Save outside the repository unless the project explicitly treats handoffs as durable artifacts. Report the path.
