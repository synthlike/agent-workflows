# Strict cross-backend record migration

Status: agreed behavior for `v0.5.0` implementation  
Decision: ARP-0010

## Purpose

Move one complete semantic record route between different supported backend types without changing semantic authority, silently dropping portable meaning, rewriting free-form content, or claiming an atomic cross-provider transaction.

Migration is an explicit workflow. Configuration, installation, and ordinary route changes never move records as a side effect.

## Scope and terminology

- A **route migration** moves exactly one of the twelve schema-3 record types from its configured source backend instance and destination to one different backend type and destination.
- A **snapshot** is a versioned, provider-neutral, revision-bound representation of one active or retained historical source record.
- **Semantic losslessness** means every source value is preserved either in an exact destination-native field or in canonical migration provenance that a destination export can retrieve and verify.
- **Canonical provenance** represents a source value that the destination cannot reproduce natively, without changing the record's exact canonical content bytes.
- A **journal** is project-contained mutable operation state for the non-atomic migration saga. It is not a new authority type.
- **Cutover** is the verified schema-3 route change from source to destination through `configure-workflows` plan/apply.
- **Retirement** makes retained source records visibly non-authoritative without deleting them.

Semantic reclassification is forbidden. An `issues` record cannot become `research`, even if both providers render records as notes or issues.

## Adapter-owned capabilities

Capability declaration schema 2 adds two independent operation lists:

- `record_migration_operations` for the eleven non-issue types;
- `issue_migration_operations` for `issues`.

Both lists draw only from:

- `export-history`: enumerate active and retained history and return complete revision-bound snapshots;
- `import`: create or resume a semantically lossless destination representation;
- `verify`: export the destination representation and compare it with the normalized source snapshot;
- `retire`: archive or tombstone a source through a revision-gated operation.

A source requires `export-history` and `retire`. A destination requires `import` and `verify`. Normal record or issue operations do not imply migration support. Empty migration lists explicitly mean unsupported. Project configuration cannot declare, add, or override adapter migration capabilities.

The installed verifier rejects unknown fields, schema versions, operation names, backend types, unsupported record types, same-type pairs, and missing role operations before source enumeration or mutation.

## Version-1 snapshot

The normative machine schema is [`migration-snapshot.schema.json`](../../backends/record-store/migration-snapshot.schema.json). A snapshot contains exactly:

- `snapshot_version: 1`;
- the unchanged semantic `record_type`;
- source backend instance/type, complete opaque structured reference, and opaque revision;
- semantic ID and provider-native ID;
- exact title and content plus SHA-256 of the UTF-8 content bytes;
- source-created and source-modified timestamps;
- explicit lifecycle state and archive flag;
- sorted provenance entries; and
- either `issue: null` or complete issue kind, status, assignee, labels, chronological comments, and structured parent/blocking relationships.

Export includes active and retained historical records. Normal list/search visibility does not define migration completeness. Comments preserve exact body, source author, source timestamp, source ID, and source reference where available. Relationships carry complete opaque target references and are recreated only after destination identity mappings exist.

Snapshot arrays use deterministic ordering:

1. records by semantic ID then source reference identity;
2. labels by Unicode code point;
3. comments by source timestamp then source ID;
4. relationships by kind then target backend and ID; and
5. provenance by classification then name then canonical JSON value.

Issue snapshots require issue state; non-issue snapshots require `issue: null`. The snapshot revision is rechecked before each source-dependent mutation and again across the complete inventory immediately before cutover.

## Provider metadata classification

Every exported value has one classification:

| Classification | Meaning | Planning behavior |
| --- | --- | --- |
| `portable-native` | Portable meaning has an exact destination-native representation. | Import and compare natively. |
| `portable-represented` | Portable meaning requires canonical migration provenance. | Import provenance and verify round-trip. |
| `provider-required` | Provider framing, scope, labels, hashes, or IDs required to operate safely. | Recreate through the adapter; never promote to semantic authority. |
| `provider-informational` | Non-authoritative provider detail retained for audit. | Preserve in the journal or canonical provenance as specified by the adapter. |
| `unsupported` | No approved destination representation exists. | Stop planning before writes. |

Canonical provenance must be deterministic, distinguish source backend/reference and field name, preserve the exact source value, remain retrievable through migration export, and leave canonical content bytes unchanged. It may use provider-native metadata, migration-owned comments, or adapter-owned framing. The project journal alone is not sufficient for portable authoritative state after source retirement.

A destination-native issue ID may differ. The journal and destination provenance retain the source reference and semantic identity. Non-issue semantic IDs must remain unchanged. Free-form Markdown links remain byte-for-byte unchanged; only structured relationships and adapter-managed references are recreated.

## Version-1 plan

The normative machine schema is [`migration-plan.schema.json`](../../backends/record-store/migration-plan.schema.json). A plan binds:

- exact consumer root and one semantic record type;
- source and destination instance/type, route destination, settings hash, immutable capability hash, and applicable preflight evidence hash;
- cooperative freeze acknowledgement and complete source inventory hash;
- every canonical snapshot and snapshot hash;
- destination absence or a previously imported exact match;
- normalized import hash and deterministic relationship ordering;
- approved project-contained journal path and expected prior hash/absence;
- exact `configure-workflows` cutover plan path/digest and source/destination route hashes;
- the three ordered stages; and
- managed directories to create and record destinations deliberately left absent.

Plan JSON is canonical UTF-8 with sorted object keys, two-space indentation, one final newline, no duplicate keys, and deterministically ordered arrays. `digest` is `sha256` over canonical plan JSON excluding only `digest`. Identical consumer/provider state and normalized intent produce byte-identical plans.

Planning is read-only. It fails without creating a journal or destination record when any input is malformed, incomplete, stale, escaping, colliding, capability-incomplete, identity-mismatched, unrepresentable, or unsupported. Provider preflight is conditional: local inspection invokes no external provider; a considered GitHub or Bear endpoint must supply current read-only identity/capability evidence.

The cutover plan is generated by installed `configure-workflows`. Migration never composes or edits `.agents/workflows.yaml`, root guidance, generated guidance, or adapter assets itself.

## Version-1 journal

The normative machine schema is [`migration-journal.schema.json`](../../backends/record-store/migration-journal.schema.json). The user approves one project-contained journal path; `.agents/migrations/` is the recommended default and is created lazily by the approved copy stage.

Each canonical journal revision binds the immutable migration plan digest and contains:

- monotonically increasing journal revision and digest;
- route type, saga state, and recovery direction;
- freeze acknowledgement, source inventory hash, and latest complete recheck time;
- separate stage approvals bound to the exact plan digest;
- each source revision, destination mapping/revision, copy state, semantic verification evidence, and retirement state/revision;
- bound configuration plan state and installed-verification evidence; and
- ordered stage events with evidence hashes.

Journal `digest` is SHA-256 over canonical JSON excluding only `digest`. Every update requires the current journal digest and writes one complete next revision. Resume first validates plan digest, journal digest/revision, installed distribution, configured source route, backend identities, capability declarations, current completed checkpoints, and stage-specific stale state. It never infers completion from a partial provider response.

The journal is operational evidence, not an RFC, ARP, specification, issue, or migrated record. It contains no provider token or secret. Paths must remain inside the consumer root and outside all installed skill directories and configured record destinations.

## Stages and approvals

Invocation and plan generation authorize no mutation. The user reviews the entire plan and separately approves each stage's exact plan digest. Canonical stage names are `copy-verify`, `route-cutover`, and `source-retirement`; abandoned pre-cutover destinations use the separate `staged-cleanup` approval.

### 1. Destination copy and verification

The source route remains authoritative. A cooperative source-route write freeze is acknowledged before the first destination write. Each import is idempotent and collision-safe. Immediately after mutation, destination export is semantically compared with the normalized snapshot before the journal checkpoint advances.

Failure leaves completed verified destinations checkpointed for resume. The workflow never automatically archives or deletes staged records. Before cutover, abandonment may offer a separate `staged-cleanup` plan and approval. Cleanup must retain auditable provenance and may use only adapter-supported retirement; native deletion is forbidden.

### 2. Route cutover

Cutover is allowed only when all destination records verify, every mapping and relationship is complete, provider identity remains unchanged, and a fresh complete source revision/inventory check matches the plan under the cooperative freeze.

The workflow invokes the bound `configure-workflows` `apply-consumer` plan and exact approved digest. Successful installed verification is journaled before authority is considered cut over. The configuration transaction changes the one selected route and its resulting exact backend assets/guidance while preserving unrelated consumer bytes.

Before verified cutover, recovery direction is `pre-cutover`. After verified cutover it changes irreversibly to `roll-forward`. The workflow never reverts the route after cutover because the destination may receive new authoritative writes.

### 3. Source retirement

Retirement rechecks the latest source revision and destination mapping for each record:

- non-issue records use metadata archive and retain direct read/reference access;
- active source issues cancel with a migration tombstone and rendered destination reference;
- resolved or cancelled source issues retain terminal state and receive a migration provenance comment; and
- source content is never rewritten or deleted.

Each result is read back and checkpointed. Partial failure resumes forward. Completion requires all source records retired, destination authority verified under current configuration, complete mappings, unchanged content hashes, installed consumer verification, and no unplanned file/provider mutation.

## Conformance matrix

The v1 target matrix is directional:

| Record type | Source | Destination | Required support |
| --- | --- | --- | --- |
| `issues` | local Markdown | GitHub | Complete issue export/retire and issue import/verify |
| `issues` | GitHub | local Markdown | Complete issue export/retire and issue import/verify |
| Any non-issue type | local Markdown | GitHub | Complete record migration roles |
| Any non-issue type | GitHub | local Markdown | Complete record migration roles |
| Any non-issue type | local Markdown | Bear | Complete record migration roles |
| Any non-issue type | Bear | local Markdown | Complete record migration roles |
| Any non-issue type | GitHub | Bear | Complete record migration roles |
| Any non-issue type | Bear | GitHub | Complete record migration roles |

Bear never accepts `issues`. Same-backend-type moves, semantic reclassification, partial-route migration, active-only migration, free-form link rewriting, source deletion, Things, and implicit configuration migration are unsupported in v1.

Capability declarations initially remain empty until each adapter passes its migration conformance issue. Therefore no real pair is eligible merely because this specification exists. Eligibility appears only as implementations land with complete declarations.

## Required verification

- Reject project-declared support and every incomplete source/destination role.
- Verify schemas reject duplicate/unknown fields, invalid versions/digests/paths, extra record types, and inconsistent issue/non-issue snapshots.
- Exercise active and historical export completeness, stable ordering, exact content hashes, comments, provenance, relationships, and opaque revisions/references.
- Exercise all matrix directions with capability-complete fixtures and reject Bear issues and same-type pairs.
- Verify planning performs no write and stale state invalidates the whole plan.
- Verify journal guarded updates, idempotent resume, partial copy, collision, ambiguous provider result, staged cleanup approval, freeze violation, and no-op checkpoints.
- Verify cutover uses exact configuration plan/apply and source retirement cannot begin before verified route authority.
- Verify post-cutover failures always resume roll-forward.
- Run normal suites with mocked providers and no live external mutation.

## References

- ARP-0010: Migrate one semantic record route through a resumable staged move
- [Record routing and backend contracts](record-routing-and-backend-contracts.md)
- [Portable record-store contract](../../backends/record-store/contract.md)
