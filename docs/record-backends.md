# Record backends

Agent Workflows routes each semantic record type independently through a named backend instance. Workflows read `.agents/workflows.yaml` and `docs/agents/records.md`, use portable operations, and treat destinations, revisions, and structured references as opaque.

Canonical contracts and implementations are under [`backends/record-store/`](../backends/record-store/):

- [portable contract](../backends/record-store/contract.md);
- [local Markdown](../backends/record-store/local-markdown.md); and
- [GitHub](../backends/record-store/github.md).

Local Markdown supports all twelve routes and creates configured destinations lazily. GitHub supports all twelve routes through managed issues, explicit identity preflight, `workflow:record:*` labels, and additional `workflow:issue:*` labels for issue-routed objects. GitHub non-issue records close as completed after publication; issue-routed objects retain native lifecycle and relationship semantics.

A configured consumer receives `docs/agents/backends/contract.py` plus exactly one guidance/helper pair per backend type used by a route. Generated copies are consumer-owned and must exactly match the reviewed installed assets at configuration time.

Backend selection and provisioning remain approval-gated. A route change does not move, copy, relabel, synchronize, or rewrite existing records.
