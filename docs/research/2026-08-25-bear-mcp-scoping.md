<!-- agent-workflows-record
{"archived":false,"created":"2026-08-25T16:11:11.894478+00:00","id":"2026-08-25-bear-mcp-scoping","modified":"2026-08-25T19:11:24Z","record_type":"research","title":"Bear MCP scoping and record storage"}
-->
# Bear MCP scoping and record storage

## Question

Can one Bear MCP server safely expose one project's workflow records through a root tag with nested record-kind tags, and which exact MCP behaviors can support the portable non-issue record contract?

## Verified facts

### Scope and transport

- Bear for Mac includes `bearcli`; the documented server command is `/Applications/Bear.app/Contents/MacOS/bearcli mcp-server`. The installed first-party binary was Bear CLI `2.9.3 (14672)` on 2026-08-25. [Bear CLI documentation](https://bear.app/faq/command-line-interface/)
- `bearcli mcp-server` speaks JSON-RPC 2.0 as line-delimited JSON on stdin/stdout. A read-only probe successfully initialized with MCP protocol `2025-06-18`, received server name `bearcli`, version `2.9.3 (14672)`, and a tools capability, then sent `notifications/initialized` before `tools/list`. This ordering follows the MCP lifecycle. [MCP lifecycle specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)
- `--only-tags TAG` restricts every read and write to notes carrying that tag or a nested child. List and search results are filtered; direct access outside the scope returns `out_of_scope`; edits that would remove a note from scope are rejected. With one included tag, `create_note` injects that tag. Bear recommends one server entry per scope. Local `bearcli mcp-server --help`, inspected 2026-08-25; [Bear CLI documentation](https://bear.app/faq/command-line-interface/).
- The initialized server echoed the exact active `onlyTags` predicate in `serverInfo.scope` and in tool results. A read-only `list_notes` call against a unique empty scope returned `total: 0`, an empty list, and the scope. No note or tag was created or changed.

### Required tools and schemas

- `create_note` accepts optional `title`, `content`, `tags`, and `ifNotExists`. It returns native note ID, canonical stored content, title, tags, timestamps, location, lock state, and other metadata, but no content hash. Its annotation is write-capable and non-idempotent. Title-based `ifNotExists` is not a semantic-ID allocator because Bear titles may be mutable and the workflow ID lives in managed metadata.
- `read_note_content` accepts native `id` or title. A whole-note read returns raw Markdown plus `hash`; reading is the only source of that hash. Byte-slice reads do not return a hash. `get_note` supplies structured metadata and optional content but not the write hash.
- `overwrite_note` requires `content` and `baseHash` through MCP. A whole-note hash rejects the write if any note content changed. The operation derives the title from the first heading and tags from hashtags, so complete overwrite content must preserve a managed title heading and managed scope/route hashtags. It also rejects undeclared attachment removal through `expectedRemovedAttachments`; tag changes are not hash-gated.
- `list_notes` and `search_notes` expose `offset`, `limit`, `total`, sorting, location, and optional content. `list_notes` can filter by one tag, where a parent includes nested children. `search_notes` accepts Bear's full query syntax. An adapter can therefore paginate until `offset >= total` rather than assume one response is complete.
- `add_tags` and `remove_tags` are idempotent. Tag insertion position follows Bear settings, while inline hashtags in supplied content are recognized without another appended copy. Nested tags use slash separators and tags may contain spaces.
- Relevant discovered tools are `create_note`, `get_note`, `read_note_content`, `list_notes`, `search_notes`, `overwrite_note`, `add_tags`, and `remove_tags`. Bear also exposes native `archive_note`, but metadata-only workflow archive does not need it. Tool schemas and read-only/destructive annotations came from the first-party server's `tools/list` response on 2026-08-25. [MCP tools specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- Tool success returns MCP `content` and `structuredContent`. A read-only missing-note probe returned `isError: true`; its text payload contained the provider error code `note_not_found`. The adapter must handle MCP transport/protocol errors separately from provider errors embedded in tool results.

### Identity, links, archive, and privacy

- Bear exposes a stable native note `id`. Its documented deep-link form is `bear://x-callback-url/open-note?id=NOTE_ID`; the `/open-note` action identifies `id` as the note's unique identifier. [Bear x-callback-url documentation](https://bear.app/faq/x-callback-url-scheme-documentation/#open-note)
- A metadata-only archive remains a normal scoped note with managed `"archived": true` content. `list_notes` defaults to active `notes`, supports raw content, and can filter the nested route tag, so normal list/search can parse and exclude archived records while direct ID reads remain available. Native `archive_note` would instead move the note to Bear's archive location and is unnecessary for this contract.
- Bear states that CLI and MCP access the local Bear database in place, send no telemetry, and cannot expose encrypted note content. Locked notes are excluded or rejected when content is requested. [Bear CLI documentation](https://bear.app/faq/command-line-interface/)

## Interpretation and implementation consequences

- Configure one server process per project as `bearcli mcp-server --only-tags WORKSPACE`; route destinations remain workspace-relative tags, composed as `WORKSPACE/ROUTE_TAG`.
- Use native note IDs only for provider access and opaque references. Store workflow semantic ID, record type, and archive state in the canonical HTML-comment metadata envelope.
- Store a managed first-level title heading and deterministic inline root/route hashtags as part of the whole-note representation. Strip that provider-owned framing when returning portable canonical content. Re-read after every create or overwrite because create returns no hash and overwrite does not mint the next revision.
- Wrap the whole-note `hash` as the opaque portable revision and pass it back as MCP `baseHash`. Do not use modified timestamps or calculate a competing revision.
- Enumerate every page under the nested route tag, include metadata-archived notes for identity collision checks, allocate the semantic ID inside create, and recheck immediately before creation. No discovered tool provides atomic semantic-ID allocation, so simultaneous clients can still race.
- Render Bear-owned references with the documented percent-encoded note-ID deep link. Cross-backend references continue to use the complete structured reference passed to the destination adapter.
- Preflight should initialize the server, validate its echoed single-workspace scope, inspect exact required tool schemas and annotations, and perform no tool that lacks `readOnlyHint: true`.

## Remaining uncertainty

- No live note was created or modified during this research. The optional approved CRUD smoke test must verify exact round-tripping of the HTML-comment metadata envelope, deterministic title/tag framing, tag placement, deep-link encoding, stale-hash error payloads, and metadata-only archive visibility against the installed Bear version.
- Bear's schemas document the needed behavior but do not promise atomic create after a separate search. The remaining collision race must stay documented.
- The exact Things MCP operation set and its ability to implement the complete issue contract require separate primary-source research. Bear issue semantics remain out of scope for the non-issue adapter.
