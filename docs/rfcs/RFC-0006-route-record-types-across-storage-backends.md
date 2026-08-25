---
id: RFC-0006
title: Route record types across storage backends
status: accepted
authors: [synthlike]
created: 2026-08-25
decision_owner: synthlike
related_arps:
  - ../decisions/ARP-0008-use-native-github-issue-relationships.md
  - ../decisions/ARP-0009-route-semantic-records-across-backends.md
---

# Route record types across storage backends

## Summary

Replace schema 2's single issue tracker and repository-path artifact model with schema 3: named backend instances plus one explicit route for every persisted semantic record type.

The configured record types are:

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

Each route records whether persistence is enabled, the named backend, and a complete backend-specific destination even when disabled. Profiles such as “all local” or “all Bear” may simplify configuration interviews, but `configure-workflows` writes the fully expanded routes without inherited defaults.

Phase 1 defines and implements backend-neutral record and issue contracts, schema 3, local Markdown as the reference adapter, and GitHub as a second complete adapter. Bear MCP and Things MCP follow as separate phases after their adapters pass the same contract suites.

## Motivation

The current configuration assumes two unrelated storage models:

- `issue_tracker.backend` chooses GitHub or local Markdown for executable work; and
- `artifacts.*.path` assumes every other durable record is a repository file.

That shape cannot express desired configurations such as:

- local Markdown for every record;
- GitHub for every record;
- GitHub issues with local research and questionnaires;
- Things issues with Bear research and meetings; or
- Bear for every record, including issues represented through structured Markdown tasks.

Workflow skills already describe semantic operations and authority. Storage should therefore be selected per semantic record type rather than embedded in workflow instructions.

## Requirements and constraints

### Record routing

- Schema 3 MUST define named backend instances independently from record routes.
- Schema 3 MUST contain exactly the twelve record routes listed in the summary.
- Every route MUST contain the common fields `enabled`, `backend`, and `destination`.
- `destination` MUST be a mapping whose complete provider-specific fields are validated by the selected adapter.
- A disabled route MUST retain its intended backend and destination and MUST prohibit persistence without approval.
- A Bear backend instance MUST use `workspace` for its project-level root tag. A Bear record destination MUST use `tag` for its child classification; it MUST NOT call the child a collection or workspace.
- Bear MCP configuration MUST scope `bearcli mcp-server` with `--only-tags` set to the configured workspace. Schema 3 does not configure excluded Bear tags initially.
- Configuration profiles MAY simplify questions but MUST expand to explicit routes before review and write.

```yaml
backends:
  local:
    type: local-markdown
    root: .
  bear:
    type: bear-mcp
    server: bear-example
    workspace: agent-workflows/example

records:
  arps:
    enabled: true
    backend: local
    destination:
      path: docs/decisions
      prefix: ARP
  research:
    enabled: true
    backend: bear
    destination:
      tag: research
```

- `specs` MUST replace `specifications` as the configuration key, default local directory name, and backend destination name. The semantic artifact remains a specification, and `author-specification` retains its name.
- Schema 3 MUST replace schema 2 outright. No compatibility reader, alias, or automated migration is required.

### Semantic authority

- Authority MUST derive from record type, not storage location.
- Moving an RFC, ARP, specification, or domain model out of Git MUST NOT change its semantic role.
- Initiative maps and decision tickets MUST remain issue structures rather than separate record types.
- Failure findings, implementation reviews, and initiative closure summaries MUST update their requesting issue or parent record rather than create competing record types.
- A prototype route owns durable prototype metadata and conclusions; executable prototype files MAY remain temporary or external.

### Backend contracts

Every backend assigned a non-issue route MUST implement the complete record contract:

1. create a typed record and allocate any required semantic identifier within that operation;
2. read complete current content and metadata plus an opaque `revision`;
3. list and search by record type, identity, title, and backend-supported metadata;
4. update only when given the matching `expected_revision`, failing stale revisions without writing;
5. preserve an imported semantic identifier only after checking for an existing owner;
6. return a stable backend-qualified reference and render it for supported destinations; and
7. archive or retire a record without silently destroying history.

Identifier allocation MUST NOT be exposed as an allocate-then-create sequence. An adapter that cannot make identifier allocation atomic MUST recheck immediately before creation, fail on collision, and document the remaining race.

A backend assigned `issues` MUST additionally implement every operation in the issue contract: create, read, list, update, comment, claim, resolve, cancel, parent, block, and frontier.

- `configure-workflows` MUST reject a route when its backend lacks a required operation.
- A limitation such as a non-atomic claim MAY be declared, but a required operation MUST NOT silently disappear or degrade into an unqueryable convention.
- Backend preflight MUST be read-only. Every external mutation remains behind the invoking workflow's approval boundary.
- Each adapter MUST have a shared conformance suite plus provider-specific tests.

### References

- Workflows MUST treat backend references as opaque values returned by adapters.
- An adapter reference MUST be a structured value containing `backend`, native `id`, display `title`, and `href` when a renderable target exists.
- `backend` and `id` MUST remain machine-readable. `href` and provider-native or Markdown rendering remain adapter responsibilities; schema 3 MUST NOT invent a universal reference-string syntax.
- Workflows MUST NOT construct file paths, GitHub issue references, Bear note titles, Things IDs, or provider URLs themselves.
- Cross-backend links MUST be rendered by the destination adapter without copying the linked record's authority.

### GitHub representation

- GitHub MAY store every record type as a GitHub issue when all routes target GitHub.
- Every managed GitHub object MUST have exactly one `workflow:record:<record-type>` label.
- An `issues` record MUST additionally have exactly one `workflow:issue:<issue-kind>` label.
- Initial issue kinds remain `initiative`, `bug`, `implementation`, `clarification`, `research`, `prototype`, and `prerequisite`.
- The reviewed label plan MUST replace the current one-dimensional `workflow:*` labels; no label migration is required.
- Native sub-issues, native dependencies, explicit authenticated login, deterministic pagination, close reasons, and claim-conflict checks from the current GitHub adapter MUST remain.
- Non-issue records MUST preserve chronological discussion separately from canonical current content and MUST use stale-write checks for body updates.
- Every non-`issues` GitHub record MUST close as `completed` immediately after successful publication. Its semantic lifecycle, including RFC draft or resolution status, MUST remain in canonical content. Closed storage records MAY still receive guarded updates and chronological comments.
- GitHub open and closed state MUST be reserved for records routed as `issues`, so non-issue storage does not pollute executable-work queries.

### Local Markdown representation

- Local Markdown MUST support all twelve record types and therefore serves as the reference adapter.
- Existing repository conventions MUST remain configurable through explicit paths, prefixes, and issue roots.
- Local stable references MUST remain repository-contained and reviewable.
- Optional directories MUST still be created lazily.

### Generated adapter assets

- `docs/agents/issue-tracker.md` MUST be removed in schema 3.
- `docs/agents/records.md` MUST describe configured routing, structured references, common record semantics, and approval boundaries.
- `docs/agents/workflows.md` MUST remain the authority table, documentation-style policy, and pointer to record routing guidance.
- `docs/agents/backends/` MUST contain one guidance file and executable helper for each backend type used by at least one route.
- Backend guidance and helpers MUST be shared by named instances of the same type. Instance identity and settings MUST remain canonical only in `.agents/workflows.yaml` and MUST be passed explicitly to helper operations.
- Installed verification MUST reject missing, unexpected, stale, or modified generated adapter helpers.

The phase-1 generated shape is:

```text
docs/agents/
├── workflows.md
├── records.md
└── backends/
    ├── local-markdown.md
    ├── local-markdown.py
    ├── github.md
    └── github.py
```

Only backend types used by configured routes appear under `backends/`.

### Future MCP adapters

- Bear MCP SHOULD scope one server per project with a stable `workspace` tag such as `agent-workflows/<project-key>`.
- The same workspace MUST be usable as a Bear UI Workspace and as the MCP server's single `--only-tags` scope.
- Bear record destinations SHOULD use nested `tag` values derived from semantic record keys rather than workflow skill names or mutable status.
- Initial Bear configuration MUST NOT expose an `exclude_tags` setting.
- Bear mutations SHOULD use note IDs and MCP stale-write tokens rather than title-only addressing.
- Things MCP MUST NOT be accepted for `issues` until primary-source research and conformance tests show that every issue operation is implemented natively or through queryable emulation.

## Non-goals

- Implementing Bear or Things in phase 1.
- Migrating schema 2 configurations, repository documents, GitHub labels, or existing backend records.
- Synchronizing or mirroring one record across several backends.
- Automatically moving a record when its route changes.
- Providing distributed transactions across backends.
- Guaranteeing atomic claims where a provider cannot offer compare-and-set semantics.
- Standardizing one harness-specific MCP configuration file.
- Treating backend search indexes, labels, tags, or task state as new sources of authority.

## Open questions

None. The decision owner resolved backend destination shape, Bear Workspace terminology, initial exclusion of `exclude_tags`, structured references, stale-write and identifier rules, GitHub non-issue state, and generated adapter assets during RFC development.

## Options

### Option A: Named backends with explicit per-record routing

Define backend instances once and route every semantic record explicitly.

Advantages:

- expresses every target configuration without workflow-specific storage logic;
- keeps credentials, MCP server names, repository identity, and project scope in one backend instance;
- makes disabled destinations and backend capability checks auditable;
- allows authority to remain semantic and backend-independent; and
- supports phased adapter delivery behind shared contracts.

Disadvantages:

- introduces a breaking schema and broad adapter refactor;
- requires cross-backend reference semantics;
- makes complete configuration more verbose; and
- exposes provider capability differences that repository paths previously hid.

### Option B: Keep separate issue and artifact backend selectors

Generalize `issue_tracker` and add one global artifact backend, with per-artifact paths or tags.

Advantages:

- resembles schema 2;
- is smaller to implement initially; and
- keeps issue semantics visibly separate.

Disadvantages:

- cannot route research and meetings to different providers;
- cannot naturally represent Bear for issues or GitHub for every record;
- encourages another schema change when mixed routing is needed; and
- preserves workflow assumptions about storage categories.

### Option C: Let each workflow configure its own backend

Put storage settings under workflow names.

Advantages:

- appears direct to users choosing one workflow at a time; and
- avoids defining a shared record taxonomy.

Disadvantages:

- several workflows read or update the same semantic record;
- workflow renames would become artifact migrations;
- authority and storage would be duplicated across configuration; and
- cross-workflow references would remain provider-specific.

### Option D: Retain schema 2 and provider-specific instructions

Continue adding exceptions to existing paths and issue guidance.

Advantages:

- avoids immediate refactoring; and
- preserves current implementation.

Disadvantages:

- cannot satisfy the target configurations coherently;
- leaves backend capability checks informal;
- couples skills to providers; and
- accumulates incompatible storage conventions.

## Recommendation

Choose Option A and implement only phase 1 in this initiative.

This is the smallest architecture that supports the stated end goal without hardcoding provider combinations. Explicit routes are verbose but reviewable, and named backend instances isolate provider identity from semantic record ownership. Local Markdown establishes the complete reference behavior; GitHub proves that authority can move outside repository files before Bear and Things add MCP-specific constraints.

## Resolution

Accepted Option A on 2026-08-25. [ARP-0009](../decisions/ARP-0009-route-semantic-records-across-backends.md) records the consequential architecture decision and supersedes ARP-0008 while preserving its incorporated GitHub identity and native-relationship constraints. Schema-3 behavior and adapter conformance are defined by the approved [record routing and backend conformance specification](../specifications/record-routing-and-backend-contracts.md). Phase-1 implementation issues may now be planned from that contract.

## Evidence

- [Bear MCP scoping and record storage](../research/2026-08-25-bear-mcp-scoping.md)
- [Artifact model](../artifact-model.md)
- [Workflow configuration schema 2](../workflow-configuration.md)
- [Issue backend contract](../../backends/record-store/contract.md)
- [Use native GitHub issue relationships](../decisions/ARP-0008-use-native-github-issue-relationships.md)
