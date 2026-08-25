# Workflow configuration

`.agents/workflows.yaml` is the single canonical configuration at the consumer workspace root. Git is optional; the root may use Git, another version-control system, or be intentionally unversioned. All configurations use schema 3. Schema 2 is unsupported.

## Schema 3

Schema 3 records named backend instances and exactly twelve explicit record routes. Every route retains `enabled`, `backend`, and a complete typed `destination`, including disabled routes.

```yaml
schema_version: 3

distribution:
  source: github.com/synthlike/agent-workflows
  version: vMAJOR.MINOR.PATCH

installation:
  selected: [clarify-intent]
  skills:
    clarify-intent: .claude/skills/clarify-intent
    configure-workflows: .claude/skills/configure-workflows

backends:
  local:
    type: local-markdown

records:
  issues: {enabled: true, backend: local, destination: {root: .project}}
  domain: {enabled: true, backend: local, destination: {path: docs/domain}}
  arps: {enabled: true, backend: local, destination: {path: docs/decisions, prefix: ARP}}
  rfcs: {enabled: true, backend: local, destination: {path: docs/rfcs, prefix: RFC}}
  specs: {enabled: true, backend: local, destination: {path: docs/specs}}
  meetings: {enabled: false, backend: local, destination: {path: docs/meetings}}
  research: {enabled: true, backend: local, destination: {path: docs/research}}
  questionnaires: {enabled: true, backend: local, destination: {path: docs/questionnaires}}
  technical_baselines: {enabled: true, backend: local, destination: {path: docs/engineering}}
  problem_framing: {enabled: true, backend: local, destination: {path: docs/product}}
  prototypes: {enabled: false, backend: local, destination: {path: docs/prototypes}}
  handoffs: {enabled: false, backend: local, destination: {path: .agents/handoffs}}
```

A GitHub backend instance requires exact provider settings and each routed destination uses its complete managed label:

```yaml
backends:
  github-main:
    type: github
    repository: acme/project
    login: octocat

records:
  issues: {enabled: true, backend: github-main, destination: {label: workflow:record:issues}}
  specs: {enabled: true, backend: github-main, destination: {label: workflow:record:specs}}
  research: {enabled: true, backend: github-main, destination: {label: workflow:record:research}}
  # The other nine explicit routes follow the same label rule.
```

Mixed configurations declare both backend types and assign each of the twelve routes explicitly. Routes on the same GitHub instance cannot reuse another record type's label. Before route approval, `configure-workflows` verifies the configured login against the actual API identity and checks GitHub Cloud, enabled Issues, write permission, complete record operations, and complete issue/native-relationship operations when `issues` is routed there. Label planning is deterministic, reviewable, stale-safe, and applied only after separate mutation approval.

The canonical key is `specs`; the semantic artifact and workflow remain “specification” and `author-specification`. Local paths must remain inside the consumer root. ARP and RFC routes require prefixes. Disabled routes prohibit persistence without approval but retain their destinations and may still permit approved temporary or external output.

A profile question may simplify the interview, but `configure-workflows` expands it into all twelve reviewed routes. It prefers existing conventions before these defaults and does not move, copy, rename, or rewrite existing records.

Schema-3 consumers generate:

- `docs/agents/records.md` with routes, operations, references, revisions, and approval boundaries;
- `docs/agents/workflows.md` with authority and documentation policy;
- `docs/agents/backends/contract.py`, shared by generated helpers;
- `docs/agents/backends/local-markdown.md` and `local-markdown.py` only when a route uses local Markdown; and
- `docs/agents/backends/github.md` and `github.py` only when a route uses GitHub.

Schema 3 does not generate provider-specific issue-tracker guidance outside `docs/agents/backends/`. Generated backend assets must exactly match the installed `configure-workflows` copies. Record directories remain lazy and are created only on the first approved write.

## Installation inventory

- `selected` records user intent, not the calculated dependency set. Names are unique and must exist in the installed distribution manifest.
- `skills` maps every harness-discovered installed skill to its consumer-root-relative directory.
- Skill paths are unique, remain inside the consumer root, and end with the corresponding skill name.
- The mapped skill set includes `configure-workflows` and the complete transitive closure of `selected`.
- Additional manifest-known skills may remain installed without silently becoming selected.
- Installer lock files are evidence only and do not replace this inventory.

## Installed lifecycle command

Run the command carried by the installed `configure-workflows` directory. The exact path depends on the harness-discovered skill location.

```bash
python3 PATH/TO/configure-workflows/references/lifecycle.py show-manifest
python3 PATH/TO/configure-workflows/references/lifecycle.py closure clarify-intent
python3 PATH/TO/configure-workflows/references/lifecycle.py inspect \
  --consumer-root . --skills-root .claude/skills
python3 PATH/TO/configure-workflows/references/lifecycle.py verify-consumer \
  --consumer-root . --skills-root .claude/skills
```

Use repeated `--skill-dir` arguments when discovery spans several parent directories. Read-only operations support canonical JSON through `--json` where relevant.

Verification checks configuration shape, identity, inventory, closure, distributed file hashes, internal links, consumer-root containment, generated guidance, and exact backend assets. Schema 3 rejects missing and unknown routes, fields, backend instances, unsupported backend contracts, malformed destinations, escaping paths, stale helpers, and obsolete issue guidance. A routed backend must declare the record type and every common operation; the `issues` route additionally requires every issue-extension operation before any backend write.

Schema-2 keys such as `issue_tracker`, `artifacts`, and `specifications` have no compatibility aliases. Configuration changes do not move, copy, relabel, or rewrite existing records. Existing content remains where it was until separately approved record work handles it.
