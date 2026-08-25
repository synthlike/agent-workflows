---
name: prepare-handoff
description: Prepare a compact handoff so another agent or session can continue work without duplicating durable artifacts. Use when work will continue in a fresh context.
disable-model-invocation: true
license: MIT
---

# Prepare Handoff

Write a compact handoff tailored to the next session's purpose. Read `.agents/workflows.yaml` when present. Save durable handoffs under the configured handoff path when repository retention is enabled. When it is disabled, save outside the repository and do not write a handoff into the repository without approval.

Include:

- the intended next outcome;
- current state and what changed in this session;
- unresolved questions and immediate next actions;
- relevant paths, issue links, branches, and commands;
- verification already performed; and
- suggested skills for the next session.

Do not duplicate specifications, RFCs, ARPs, maps, issues, commits, or diffs. Link them. Redact credentials, secrets, and unnecessary personal information.

Report the path. Create the configured directory only when writing its first approved handoff.
