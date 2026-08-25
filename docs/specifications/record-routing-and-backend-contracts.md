# Record routing and backend conformance

## Problem

Agent Workflows currently configures one issue backend separately from repository-relative artifact paths. Workflows therefore assume that issues and documents have different storage classes and cannot express all-local, all-GitHub, mixed local/GitHub, or future Bear and Things routing per semantic record type.

Users need to choose persistence independently for every durable record without changing its authority, teaching workflows provider APIs, or accepting silently degraded backend behavior.

## Desired behavior

`configure-workflows` writes one reviewed schema-3 configuration containing named backend instances and an explicit route for every supported record type. Workflows invoke backend-neutral adapters for persistence and issue operations. Local Markdown and GitHub implement the complete phase-1 contracts and pass the same conformance suite. Configuration rejects unsupported routes before any artifact is written.

## Requirements

### Configuration schema

1. `.agents/workflows.yaml` MUST use `schema_version: 3`. Schema 2 MUST be unreadable and unsupported after the phase-1 change.
2. `distribution` and `installation` MUST retain their current immutable distribution identity, explicit workflow selection, complete discovered skill inventory, and mandatory `configure-workflows` closure semantics.
3. The configuration MUST define a non-empty `backends` mapping. Each key is a unique backend instance name and each value contains a supported `type` plus complete provider settings.
4. Phase 1 MUST support backend types `local-markdown` and `github`.
5. A GitHub instance MUST contain an explicit `repository` in `OWNER/REPO` form and `login`. Its preflight MUST retain the current GitHub Cloud, active identity, permission, enabled-Issues, native-sub-issue, and native-dependency requirements.
6. The configuration MUST define exactly these record keys:
   - `issues`;
   - `domain`;
   - `arps`;
   - `rfcs`;
   - `specs`;
   - `meetings`;
   - `research`;
   - `questionnaires`;
   - `technical_baselines`;
   - `problem_framing`;
   - `prototypes`; and
   - `handoffs`.
7. Every record route MUST contain `enabled`, `backend`, and `destination`, even when disabled.
8. `enabled` MUST be Boolean. `backend` MUST reference a configured instance. `destination` MUST be a non-empty mapping accepted by that instance's adapter for the record type.
9. Local Markdown destinations MUST use consumer-root-contained relative paths. `arps` and `rfcs` MUST additionally define non-empty prefixes. The local `issues` destination MUST define its issue root.
10. GitHub destinations MUST define their complete managed record label. Routes using the same GitHub instance MUST not claim conflicting labels.
11. Unknown backend settings, record keys, route fields, and destination fields MUST fail validation rather than be ignored.
12. Profiles MAY simplify the configuration interview, but the reviewed and written configuration MUST contain all backend instances and all twelve expanded record routes without profile inheritance.
13. The canonical specification key and default local destination MUST be `specs` and `docs/specs`. The semantic artifact and workflow remain “specification” and `author-specification`.

An illustrative mixed configuration is:

```yaml
schema_version: 3

distribution:
  source: github.com/synthlike/agent-workflows
  version: vMAJOR.MINOR.PATCH

installation:
  selected: [research-question]
  skills:
    configure-workflows: .agents/skills/configure-workflows
    research-question: .agents/skills/research-question

backends:
  local:
    type: local-markdown
  github:
    type: github
    repository: synthlike/example
    login: synthlike

records:
  issues:
    enabled: true
    backend: github
    destination: {label: workflow:record:issues}
  domain:
    enabled: true
    backend: local
    destination: {path: docs/domain}
  arps:
    enabled: true
    backend: local
    destination: {path: docs/decisions, prefix: ARP}
  rfcs:
    enabled: true
    backend: local
    destination: {path: docs/rfcs, prefix: RFC}
  specs:
    enabled: true
    backend: local
    destination: {path: docs/specs}
  meetings:
    enabled: false
    backend: local
    destination: {path: docs/meetings}
  research:
    enabled: true
    backend: local
    destination: {path: docs/research}
  questionnaires:
    enabled: true
    backend: local
    destination: {path: docs/questionnaires}
  technical_baselines:
    enabled: true
    backend: local
    destination: {path: docs/engineering}
  problem_framing:
    enabled: true
    backend: local
    destination: {path: docs/product}
  prototypes:
    enabled: false
    backend: local
    destination: {path: docs/prototypes}
  handoffs:
    enabled: false
    backend: local
    destination: {path: .agents/handoffs}
```

### Configuration workflow

14. `configure-workflows` MUST begin with provider-neutral inspection of existing workflow configuration and guidance, record locations, version-control state and workspace boundary, distribution integrity, and project structure.
15. It MUST then use one project/collaboration profile sequence to gather only intent unresolved by inspection, asking about desired persistence in semantic record terms rather than workflow names.
16. It MUST recommend existing conventions before toolkit defaults.
17. It MUST inspect remotes, authenticated accounts, provider capabilities, labels, MCP executables, or MCP scopes only for external backends the user is considering. A local-only profile MUST NOT invoke an external-backend tool.
18. It MUST validate every expanded route against backend capabilities before presenting a dry run. Local file generation MUST be represented by a versioned canonical plan that binds immutable distribution identity, normalized intent and installation inventory, exact generated text, copied-asset source and destination hashes, every target's expected prior state, managed directories to create, lazy record destinations left absent, and a `sha256` digest over the plan excluding only that digest. Planning MUST reject stale or invalid input without writes. The complete dry run MUST also show detected version-control state, chosen consumer root, landing-checkpoint behavior, applicable backend preflight results, external provisioning plans, and every consumer-workspace or external mutation.
19. No generated file, label, backend record, or external configuration MAY be changed before explicit approval. One approval MUST authorize the exact reviewed local-file plan as a whole; per-file approvals MUST NOT be requested. Applying that plan MUST require its exact reviewed digest; reject non-canonical, altered, stale, escaping, incomplete, or installation-mismatched plans before consumer writes; stage all output on the destination filesystem; write only planned configuration, guidance, and adapter assets; preserve unrelated root guidance; run installed consumer verification; and roll back prior targets and newly created planned directories on caught failure. It MUST NOT modify skill directories or create record destinations. Provider provisioning, including GitHub labels, remains a separate approved operation.
20. A disabled route MUST prohibit persistence without approval. Temporary or external output MAY still occur where the workflow permits it. Git MUST NOT be required for configuration or workflow execution. When no version-control system is detected, `configure-workflows` MUST ask whether the workspace is intentionally unversioned, explain the missing history and commit checkpoint, and MUST NOT initialize version control without approval. When version control exists, it MUST preserve that system's conventions rather than assume Git.

### Record contract

21. Every adapter receiving a non-`issues` route MUST implement the following record operations:
   1. create a typed record and allocate any required semantic identifier within that operation;
   2. read complete current content and metadata plus an opaque revision;
   3. list and search by type, identity, title, and supported metadata;
   4. update only with a matching expected revision;
   5. preserve an imported semantic identifier only after checking for an existing owner;
   6. return and render a stable reference; and
   7. archive or retire without silently destroying history.
22. A stale expected revision MUST fail without any write.
23. Identifier allocation MUST NOT be exposed as allocate-then-create. A backend lacking atomic allocation MUST immediately recheck, fail on collision, and document the remaining race.
24. A record reference MUST be a structured value containing backend instance, native stable ID, display title, and optional renderable href.
25. Workflows MUST treat references and revisions as opaque. They MUST NOT construct paths, provider IDs, URLs, Bear titles, Things IDs, or rendered links.
26. The destination adapter MUST render cross-backend references without copying the linked record's authority.
27. Authority MUST derive from record type, not backend or rendered representation.

### Issue contract

28. An adapter receiving the `issues` route MUST implement create, read, list, update, comment, claim, resolve, cancel, parent, block, and frontier while preserving the record contract's revision, reference, allocation, collision, and retained-history guarantees. It need not expose the separate non-issue record-operation interface.
29. Initiative maps and decision tickets MUST remain issue structures. They MUST NOT become separate record routes.
30. Failure findings, implementation reviews, and initiative closure summaries MUST update the requesting issue or parent record rather than create separate report records.
31. A backend limitation such as non-atomic claiming MAY be declared, but every required operation MUST remain queryable and testable.
32. `configure-workflows` MUST reject `issues` routing when any required issue operation is absent.

### Workflow behavior

33. Skills MUST resolve persistence only through the configured record route and generated adapter guidance.
34. Skills MUST use record keys, operations, references, and revisions rather than provider tools, repository paths, labels, tags, or IDs.
35. `prototype-design` MUST route durable metadata and conclusions; executable prototype files MAY remain temporary or external.
36. Existing approval, authority-promotion, confidentiality, and lazy-creation boundaries MUST remain.
37. Route changes MUST NOT move or duplicate existing records automatically.

### Local Markdown adapter

38. Local Markdown MUST implement all twelve record types and the complete issue contract, serving as the reference adapter.
39. Record revisions MUST derive from the exact current persisted content and metadata.
40. All local destinations and rendered relative links MUST remain inside the consumer root.
41. Required directories MUST be created only with the first approved record write.
42. Existing local issue status, comment, parent, blocker, and frontier semantics MUST remain behaviorally compatible.
43. The local adapter MUST surface duplicate identifiers, stale revisions, malformed records, broken references, and unsupported destination settings without mutation.

### GitHub adapter

44. GitHub MAY receive any or all twelve routes.
45. Every managed GitHub object MUST have exactly one `workflow:record:<record-key>` label.
46. A managed object routed as `issues` MUST additionally have exactly one `workflow:issue:<kind>` label. Initial kinds are `initiative`, `bug`, `implementation`, `clarification`, `research`, `prototype`, and `prerequisite`.
47. The label plan MUST replace the current one-dimensional labels. It MUST remain deterministic, stale-safe, completely reviewable, and approval-gated.
48. GitHub record reads MUST return a revision suitable for rejecting stale body or metadata updates.
49. Every non-`issues` GitHub record MUST close as `completed` immediately after successful publication. Semantic lifecycle state MUST remain in canonical content.
50. Closed non-issue records MAY receive revision-gated canonical updates and chronological comments.
51. Open and closed GitHub state MUST represent lifecycle only for records routed as `issues`.
52. Existing explicit-login verification, actual API identity check, native sub-issues, native dependencies, pagination, close reasons, relationship ID handling, idempotent relationships, and claim-conflict behavior MUST remain.
53. Search and identifier allocation MUST include open and closed records and MUST not confuse pull requests with managed records.

### Generated guidance and helpers

54. Schema 3 MUST remove `docs/agents/issue-tracker.md`.
55. `docs/agents/records.md` MUST describe configured routes, common operations, references, revisions, and approval boundaries.
56. `docs/agents/workflows.md` MUST retain the authority table, documentation policy, and pointer to record routing guidance.
57. `docs/agents/backends/` MUST contain one guidance file and executable helper per backend type used by at least one route.
58. Backend helpers MUST be shared by named instances of the same type. Instance settings remain canonical only in `.agents/workflows.yaml` and MUST be passed explicitly to every helper operation.
59. Installed verification MUST reject missing, unexpected, stale, or modified generated adapter helpers.
60. Phase-1 generated assets MUST use `local-markdown.md`, `local-markdown.py`, `github.md`, and `github.py` names as applicable.

### Verification and ownership

61. The complete record contract and issue extension MUST have backend-independent conformance suites.
62. Each adapter MUST additionally test provider-specific preflight, destination validation, references, revisions, identifier behavior, and error handling.
63. Verification MUST remain runnable from the installed `configure-workflows` assets without a distribution checkout.
64. Consumer configuration, generated guidance and helpers, backend state, and persisted records remain consumer-owned.
65. Distribution updates MUST NOT rewrite those consumer-owned files automatically. A changed bundled adapter requires a separate reviewed consumer update.
66. Verification MUST reject schema 2, partial route maps, unknown backends, unsupported routes, mismatched generated assets, escaping local paths, malformed references, and stale writes.

### Explicit route migration

67. Configuration, installation, and ordinary route changes MUST NOT move existing records implicitly.
68. Explicit cross-backend movement MUST follow the [strict record migration specification](strict-record-migration.md), preserve one semantic type, include retained history, and use separately approved copy/verify, route-cutover, and source-retirement stages.
69. Migration eligibility MUST derive only from schema-2 adapter-owned `record_migration_operations` and `issue_migration_operations`; project configuration MUST NOT declare support.
70. Migration plans and journals MUST be canonical, digest-bound, project-contained, stale-safe, resumable, and honest about cooperative freeze and non-atomic cross-provider recovery.
71. Route cutover MUST reuse deterministic `configure-workflows` plan/apply. After verified cutover, recovery MUST roll forward.

## Constraints and decisions

- RFC-0006 selects named backends and explicit per-record routing.
- ARP-0009 supersedes ARP-0008 while retaining its incorporated GitHub identity and native-relationship constraints.
- Schema 3 was an atomic configuration-schema replacement rather than a schema migration. Later explicit record migration does not restore schema-2 compatibility.
- Backend contracts describe semantic behavior; backend documents and helpers own concrete provider tools and storage.
- Bear uses a project `workspace` and nested record `tag` destinations in a later phase. Initial Bear configuration does not include `exclude_tags`.
- MCP configuration remains harness-independent; no universal MCP client file is mandated.

## Verification

- **Schema replacement:** Reject every schema-2 fixture and accept only a complete schema-3 backend and route map.
- **Explicit routing:** Expand all-local, all-GitHub, and mixed profile interviews into twelve complete routes with no inherited defaults.
- **Capability rejection:** Route `issues` to an adapter missing one issue operation and verify configuration fails before writes.
- **Disabled route:** Attempt persistence through a disabled route and verify no backend or repository mutation occurs without approval.
- **Local conformance:** Run every record and issue operation against a temporary consumer, including identifier collision, stale revision, lazy directory, relationship, frontier, and cross-record link scenarios.
- **GitHub conformance:** Use deterministic mocked API fixtures for all record kinds, both label dimensions, pagination, stale revisions, non-issue closure, native relationships, close reasons, and identity mismatch.
- **Reference behavior:** Link local and GitHub records in both directions and verify adapters preserve backend, native ID, title, and href while workflows remain provider-neutral.
- **Generated assets:** Verify exactly the helpers required by configured backend types, exact bundled content, matching guidance, and no obsolete issue-tracker guidance.
- **Installed lifecycle:** Copy installed assets without the source checkout and verify complete schema-3 inspection and conformance entrypoints.
- **No implicit migration:** Verify configuration alone does not rename, move, copy, or rewrite existing records or labels. Explicit migration uses the separately approved strict migration contract.

## Out of scope

- Bear MCP implementation.
- Things MCP implementation.
- Schema-2 compatibility or automated migration.
- Implicit record or GitHub label migration during configuration.
- Cross-backend mirroring or synchronization.
- Atomic distributed transactions across backends.
- Initializing, migrating, or configuring a version-control system.
- Atomic claiming where the provider has no compare-and-set operation.
- Harness-specific MCP configuration management.
- New semantic authority types or standalone failure, review, and closure reports.

## Open items

- Research and specify Bear record and issue conformance after phase 1.
- Research the Things MCP operation set before accepting it for `issues`.
- Decide release numbering during release planning; this specification does not assign a version.

## References

- [RFC-0006: Route record types across storage backends](../rfcs/RFC-0006-route-record-types-across-storage-backends.md)
- [ARP-0009: Route semantic records across backends](../decisions/ARP-0009-route-semantic-records-across-backends.md)
- [ARP-0010: Migrate one semantic record route through a resumable staged move](../decisions/ARP-0010.md)
- [Strict cross-backend record migration](strict-record-migration.md)
- [ARP-0008: Use native GitHub issue relationships](../decisions/ARP-0008-use-native-github-issue-relationships.md)
- [Bear MCP scoping and record storage](../research/2026-08-25-bear-mcp-scoping.md)
- [Artifact model](../artifact-model.md)
- [Issue backend contract](../../backends/record-store/contract.md)

### Phase-1 implementation

- [Persist one routed record through the portable contract](../../.project/issues/ISSUE-0035-persist-one-routed-record-through-the-portable-contract.md)
- [Complete the local Markdown reference adapter](../../.project/issues/ISSUE-0036-complete-the-local-markdown-reference-adapter.md)
- [Configure and verify an all-local schema-3 consumer](../../.project/issues/ISSUE-0037-configure-and-verify-an-all-local-schema-3-consumer.md)
- [Route existing workflows through record adapters](../../.project/issues/ISSUE-0038-route-existing-workflows-through-record-adapters.md)
- [Generalize GitHub to all record types](../../.project/issues/ISSUE-0039-generalize-github-to-all-record-types.md)
- [Configure all-GitHub and mixed schema-3 consumers](../../.project/issues/ISSUE-0040-configure-all-github-and-mixed-schema-3-consumers.md)
- [Cut over atomically to schema 3](../../.project/issues/ISSUE-0041-cut-over-atomically-to-schema-3.md)
- [Validate phase-1 backend conformance end to end](../../.project/issues/ISSUE-0042-validate-phase-1-backend-conformance-end-to-end.md)
