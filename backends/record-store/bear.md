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

Each routed non-issue record uses one workspace-relative nested tag:

```yaml
records:
  specs:
    enabled: true
    backend: notes
    destination: {tag: specs}
```

The adapter composes `agent-workflows/project-key/specs`. Tags must be trimmed relative names without a leading `#` or `/`, empty or dot segments, commas, backslashes, or repetition of the workspace.

## Read-only preflight

Run preflight before recommending or approving any Bear route:

```bash
python3 docs/agents/backends/bear.py \
  --command /Applications/Bear.app/Contents/MacOS/bearcli \
  --workspace agent-workflows/project-key preflight
```

The helper launches exactly `COMMAND mcp-server --only-tags WORKSPACE`, initializes MCP protocol `2025-06-18`, verifies the `bearcli` identity and echoed single-tag scope, and inspects `tools/list`. It requires scoped create, metadata read, whole-note hash read, paginated list/search, `baseHash` overwrite, and add/remove tag schemas with appropriate read-only annotations.

Preflight calls no Bear tools and creates or changes no note or tag. A successful result establishes provider capability only. Until the Bear adapter declares and passes the common record operations, installed verification still rejects Bear routes.

## Safety and limitations

Configuration and every later mutation remain approval-gated. The helper does not add a harness MCP registration and does not discover a command from `PATH`. Bear is optional and normal repository verification does not launch it. Encrypted note content is unavailable through Bear MCP. Bear record CRUD and live mutation are implemented in later initiative slices.
