# Record backends

Agent Workflows routes each semantic record type independently through a named backend instance. Workflows read `.agents/workflows.yaml` and `docs/agents/records.md`, use portable operations, and treat destinations, revisions, and structured references as opaque.

Canonical contracts and implementations are under [`backends/record-store/`](../backends/record-store/). Each adapter owns a schema-1 `<type>.capabilities.json` declaration beside its implementation; installed verification reads the immutable distributed copy rather than trusting project configuration.

- [portable contract](../backends/record-store/contract.md);
- [local Markdown](../backends/record-store/local-markdown.md);
- [GitHub](../backends/record-store/github.md); and
- [Bear MCP](../backends/record-store/bear.md).

Local Markdown supports all twelve routes and creates configured destinations lazily. GitHub supports all twelve routes through managed issues, explicit identity preflight, `workflow:record:*` labels, and additional `workflow:issue:*` labels for issue-routed objects. Bear supports the eleven non-issue routes through a project-scoped MCP server, whole-note hash revisions, managed metadata, workspace-relative tags, and read-only provider preflight; it does not support `issues`. GitHub non-issue records close as completed after publication; issue-routed objects retain native lifecycle and relationship semantics.

A configured consumer receives `docs/agents/backends/contract.py` plus exactly one guidance/helper pair per backend type used by a route. Generated copies are consumer-owned and must exactly match the reviewed installed assets at configuration time.

## Conformance and limitations

Local Markdown and GitHub run the same backend-independent record and issue-extension suites; Bear runs the shared non-issue record suite. Installed-consumer tests cover all-local, all-GitHub, local/GitHub mixed, Bear-plus-local, and Bear-plus-GitHub routes; exact generated assets; disabled routes; capability rejection; cross-backend references; and source-checkout-free verification. GitHub and Bear provider behavior is tested with deterministic mocked responses rather than writes to live stores. Normal verification never launches `bearcli`.

## Optional Bear verification

`scripts/smoke-bear-preflight.sh` validates the installed Bear identity, exact scoped MCP predicate, tool schemas, and annotations without calling a Bear tool. It exits successfully with an explicit skipped result when Bear is unavailable; set `BEARCLI_REQUIRED=1` when absence should fail.

`scripts/smoke-bear-crud.sh` refuses to run unless `BEAR_CRUD_APPROVED=YES` and `BEAR_SMOKE_WORKSPACE` names a unique child of `agent-workflows-smoke/`. It verifies create, read, query search, revision-gated update, stale-write rejection, metadata-only archive, and active-search exclusion. The final result reports that the note is metadata-archived and retained; it does not delete the native note or workspace tag. See the [Bear backend guidance](../backends/record-store/bear.md) for exact commands, managed framing, revision and reference semantics, concurrency boundaries, and ambiguous-failure recovery.

Configuration rejects a routed backend unless its adapter-owned declaration includes the routed record type and its complete required operation set: common record operations for non-issue routes or the issue extension for `issues`. Generated helpers assume the workflow has already resolved an enabled route and obtained approval; they intentionally do not discover configuration or enforce conversational approval themselves. Workflows must not invoke a mutation helper for a disabled route without new approval.

Local allocation and claiming are serialized only within one workspace and are not atomic across unsynchronized working trees. GitHub behavior depends on the authenticated account, repository permissions, API availability, and native sub-issue and dependency support established by preflight.

Backend selection and provisioning remain approval-gated. A route change does not move, copy, relabel, synchronize, or rewrite existing records.
