---
id: ISSUE-0058
title: "Implement strict cross-backend record migration"
kind: "initiative"
status: open
created: 2026-08-25
assignee: 
parent: 
blocked_by:
labels: ["migration","record-routing"]
---
# Implement strict cross-backend record migration

## Destination

A user can explicitly invoke `/skill:migrate-records` to move one complete semantic record route between capability-compatible local Markdown, GitHub, and Bear backends without changing record type, losing portable meaning, guessing at unsupported fidelity, or pretending cross-provider writes are atomic.

## Success criteria

- The manually invoked distributed skill is discoverable but excluded from model invocation; natural-language migration requests direct the user to invoke it explicitly.
- One migration handles exactly one semantic route and includes active and retained historical records.
- `issues` supports local Markdown ↔ GitHub; every non-issue type supports all lossless pairs among local Markdown, GitHub, and Bear.
- Adapter-owned migration capabilities expose complete historical export and semantic-lossless import without weakening normal record contracts.
- Plans bind source revisions, destination collision/absence state, exact normalized snapshots, provider identity/preflight evidence, configuration-plan identity, and a canonical digest.
- An approved project-contained journal, defaulting to `.agents/migrations/`, supports idempotent resume and records source/destination references, stage evidence, cutover, and retirement progress.
- Destination copy/verification, deterministic route cutover, and source retirement require separate approvals.
- Route cutover reuses `configure-workflows` plan/apply; migration never hand-edits configuration or generated guidance.
- Source content remains byte-for-byte unchanged; free-form links are not rewritten. Structured relationships and adapter-managed references are recreated.
- Non-issue IDs remain stable. Destination-native issue IDs may change only with durable source-to-destination mapping and provenance.
- Semantic losslessness preserves every source value natively or in canonical migration provenance and rejects any unrepresentable value before writes.
- Migration uses a cooperative source write freeze plus revision rechecks. Any pre-cutover change blocks cutover.
- Before cutover, abandoned staged destinations may be cleaned only through separate approval. After cutover, recovery always rolls forward.
- Non-issue sources retire through metadata archive. Active source issues cancel with a migration tombstone; terminal issues retain state and receive provenance.
- The complete feature ships in the single immutable `v0.5.0` release with the already completed schema-3, Bear, discovery, template, and plan/apply work.

## Decisions so far

- Preserve semantic record type strictly; reclassification is unsupported.
- Move one complete route per plan, including active and historical records.
- Reject migrations that cannot preserve portable meaning.
- Preserve content bytes and do not heuristically rewrite embedded links.
- Use semantic-lossless canonical provenance where provider-native fidelity is impossible.
- Keep non-issue semantic IDs; map provider-assigned issue IDs durably.
- Use three separately approved stages: destination copy/verification, route cutover, and source retirement.
- Reuse deterministic consumer configuration plan/apply for route cutover.
- Journal the non-atomic saga in an approved project-contained location.
- Require a cooperative source write freeze and complete revision recheck before cutover.
- Roll forward after successful cutover.
- Distribute `migrate-records` with `disable-model-invocation: true`; natural-language requests instruct explicit invocation.

## Execution plan

- Specify portable migration snapshots and capability declarations.
- Implement lossless export/import for local Markdown, GitHub, and Bear.
- Generate revision-bound plans and durable resumable journals.
- Apply destination copy and semantic verification resumably.
- Cut over routes through configuration plan/apply and retire sources safely.
- Add the manual skill, full matrix conformance, source-checkout-free scenarios, failure recovery, and release documentation.

## Not yet specified

None.

## Out of scope

- Semantic record-type reclassification.
- Heuristic rewriting of free-form content links.
- Deleting source records or native Bear notes.
- Cross-provider atomicity or an unenforceable distributed lock.
- Automatic model invocation, implicit migration during configuration, and provider mutation without exact approval.
- Things implementation.

## Comments


## Resolution
