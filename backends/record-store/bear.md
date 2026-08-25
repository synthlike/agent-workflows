# Record store: Bear MCP

The Bear backend scopes one `bearcli mcp-server` process to a project workspace tag. It is intended for the eleven non-issue semantic record types; it never implements the `issues` extension.

## Configuration

A backend instance requires an explicit absolute executable and one project workspace tag:

```yaml
backends:
  notes:
    type: bear
    command: /Applications/Bear.app/Contents/MacOS/bearcli
    workspace: agent-workflows/project-key
```

Each routed non-issue record uses one workspace-relative nested tag. `issues` must use a complete local Markdown or GitHub issue backend:

```yaml
backends:
  local:
    type: local-markdown
  notes:
    type: bear
    command: /Applications/Bear.app/Contents/MacOS/bearcli
    workspace: agent-workflows/project-key

records:
  issues:
    enabled: true
    backend: local
    destination: {root: .project}
  specs:
    enabled: true
    backend: notes
    destination: {tag: specs}
```

The actual configuration must still contain all twelve explicit routes. See the distribution's complete `examples/bear-local/workflows.yaml` example. Bear never supports `issues`; route verification rejects that assignment before any provider operation.

The adapter composes `agent-workflows/project-key/specs`. Tags must be trimmed relative names without a leading `#` or `/`, empty or dot segments, commas, backslashes, or repetition of the workspace.

## Read-only preflight

Run preflight before recommending or approving any Bear route:

```bash
python3 docs/agents/backends/bear.py \
  --command /Applications/Bear.app/Contents/MacOS/bearcli \
  --workspace agent-workflows/project-key preflight
```

The helper launches exactly `COMMAND mcp-server --only-tags WORKSPACE`, initializes MCP protocol `2025-06-18`, verifies the `bearcli` identity and echoed single-tag scope, and inspects `tools/list`. It requires scoped create, metadata read, whole-note hash read, paginated list/search, `baseHash` overwrite, and add/remove tag schemas with appropriate read-only annotations.

Preflight calls no Bear tools and creates or changes no note or tag. Route approval additionally requires the immutable Bear adapter declaration to contain the routed type and every common record operation.

## Records

The adapter supports create, read, paginated list/search, revision-gated update, metadata-only archive, and reference rendering for all eleven non-issue record types. Pass the named backend and route tag explicitly:

```bash
python3 docs/agents/backends/bear.py \
  --command /Applications/Bear.app/Contents/MacOS/bearcli \
  --workspace agent-workflows/project-key \
  --backend notes --destination-tag research \
  record-create --record-type research --title "Finding" --content-file finding.md
```

Use the returned semantic ID and opaque `bear-base-hash:*` revision for later operations:

```bash
python3 docs/agents/backends/bear.py --command /Applications/Bear.app/Contents/MacOS/bearcli \
  --workspace agent-workflows/project-key --backend notes --destination-tag research \
  record-read --record-type research finding
python3 docs/agents/backends/bear.py --command /Applications/Bear.app/Contents/MacOS/bearcli \
  --workspace agent-workflows/project-key --backend notes --destination-tag research \
  record-update --record-type research finding --expected-revision 'bear-base-hash:...' \
  --content-file revised.md
```

Managed notes retain semantic ID, type, and archive state in this canonical framing (values shown illustratively):

```markdown
<!-- agent-workflows-record:{"archived":false,"id":"finding","record_type":"research"} -->
# Finding

Canonical workflow content.

<!-- agent-workflows-tags -->
#agent-workflows/project-key #agent-workflows/project-key/research
```

Provider-owned framing preserves the compact sorted metadata envelope, first-level title, tag marker, and both workspace hashtags through whole-note overwrite. The adapter paginates every note under the nested route tag, parses managed metadata, rechecks semantic IDs immediately before create, and re-reads after every mutation to obtain the next Bear hash. Archive changes managed metadata rather than moving the note into Bear's native Archive.

Returned references retain the native note ID and use Bear's documented `bear://x-callback-url/open-note?id=...` deep link. `render-reference` accepts complete structured references from any backend without launching MCP.

## Failure and recovery behavior

Read, list/search, update, and archive fail closed on malformed managed metadata, missing scope tags, unavailable encrypted content, MCP/provider errors, or unexpected response shape. Update and archive compare the caller's opaque revision with a fresh whole-note hash before sending `overwrite_note`; Bear then enforces the same hash as `baseHash`. A stale operation performs no adapter write. Managed records with attachments reject overwrite and archive rather than risk undeclared attachment removal.

After every successful mutation, the adapter re-reads the note and returns its current revision. If a process or transport failure makes a result ambiguous, do not invent a revision or blindly repeat the mutation: read/search the semantic ID in the same scoped route and reconcile the returned content first. Create checks all archived and active managed IDs twice before calling Bear, so a retry after an ambiguous create should first search that ID. Allocation is still not atomic across simultaneous clients; one disposable duplicate may require manual review if two clients pass both checks concurrently.

Metadata archive sets `"archived": true` through a hash-gated overwrite. The note remains in the scoped Bear database and is available by direct read, but normal list/search excludes it. Archive is therefore retained cleanup, not deletion. The adapter cannot roll back an already accepted provider mutation after an uncatchable process or machine failure.

## Optional live verification

The read-only smoke preflight calls no Bear tools. It skips successfully when Bear is unavailable, or can require Bear explicitly:

```bash
scripts/smoke-bear-preflight.sh
BEARCLI_REQUIRED=1 BEAR_WORKSPACE=agent-workflows/preflight \
  scripts/smoke-bear-preflight.sh
```

Live CRUD is never part of normal verification. Review a unique disposable workspace, then provide both the exact approval sentinel and workspace:

```bash
BEAR_CRUD_APPROVED=YES \
BEAR_SMOKE_WORKSPACE=agent-workflows-smoke/UNIQUE-ID \
  scripts/smoke-bear-crud.sh
```

The CRUD smoke verifies create, read, query search, revision-gated update, stale-write rejection, metadata archive, and exclusion from active search. Its final JSON reports the cleanup state and retained native note. It deliberately does not delete the note or workspace tag.

## Safety and limitations

Configuration and every mutation remain approval-gated. The helper does not add a harness MCP registration and does not discover a command from `PATH`. Bear is optional. Normal repository verification uses mocked MCP responses, neither launches Bear nor mutates a Bear database, and does not run either live smoke script. Encrypted note content is unavailable through Bear MCP. Semantic-ID allocation rechecks before create but remains non-atomic across simultaneous clients.
