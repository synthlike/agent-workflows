---
name: research-question
description: Investigate a focused question using high-trust primary sources and save concise cited findings. Use when a design or decision depends on facts outside the current repository.
license: MIT
---

# Research Question

Investigate one focused question.

Read `.agents/workflows.yaml` when present. Use the configured research path when repository retention is enabled. When it is disabled, do not write research into the repository without approval; use an approved external or temporary location instead.

1. State the question and what decision it will inform.
2. Prefer primary sources: official documentation, specifications, source code, standards, and first-party APIs.
3. Trace material claims to the source that owns them.
4. Distinguish verified facts, interpretations, and remaining uncertainty.
5. Write concise findings to the configured research location, or to the approved external or temporary location when repository retention is disabled.
6. Link the findings from the requesting artifact rather than copying them into several places.

Research informs decisions but does not make them. Do not turn a recommendation into an accepted decision without the decision owner's confirmation.
