# Record backends

Agent Workflows routes each semantic record type independently through a named backend instance. Workflows read `.agents/workflows.yaml` and `docs/agents/records.md`, use portable operations, and treat destinations, revisions, and structured references as opaque.

Canonical contracts and implementations are under [`backends/record-store/`](../backends/record-store/). Each adapter owns a schema-1 `<type>.capabilities.json` declaration beside its implementation; installed verification reads the immutable distributed copy rather than trusting project configuration.

- [portable contract](../backends/record-store/contract.md);
- [local Markdown](../backends/record-store/local-markdown.md); and
- [GitHub](../backends/record-store/github.md).

Local Markdown supports all twelve routes and creates configured destinations lazily. GitHub supports all twelve routes through managed issues, explicit identity preflight, `workflow:record:*` labels, and additional `workflow:issue:*` labels for issue-routed objects. GitHub non-issue records close as completed after publication; issue-routed objects retain native lifecycle and relationship semantics.

A configured consumer receives `docs/agents/backends/contract.py` plus exactly one guidance/helper pair per backend type used by a route. Generated copies are consumer-owned and must exactly match the reviewed installed assets at configuration time.

## Conformance and limitations

Local Markdown and GitHub run the same backend-independent record and issue-extension suites. Installed-consumer tests cover all-local, all-GitHub, and mixed routes; exact generated assets; disabled routes; capability rejection; cross-backend references; and source-checkout-free verification. GitHub provider behavior is tested with deterministic mocked API responses rather than writes to a live repository.

Configuration rejects a routed backend unless its adapter-owned declaration includes the routed record type and its complete required operation set: common record operations for non-issue routes or the issue extension for `issues`. Generated helpers assume the workflow has already resolved an enabled route and obtained approval; they intentionally do not discover configuration or enforce conversational approval themselves. Workflows must not invoke a mutation helper for a disabled route without new approval.

Local allocation and claiming are serialized only within one workspace and are not atomic across unsynchronized working trees. GitHub behavior depends on the authenticated account, repository permissions, API availability, and native sub-issue and dependency support established by preflight.

Backend selection and provisioning remain approval-gated. A route change does not move, copy, relabel, synchronize, or rewrite existing records.
