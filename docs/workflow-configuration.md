# Workflow configuration schema 2

`.agents/workflows.yaml` is the single canonical configuration at the consumer Git root. Schema 2 records installation intent and discovered paths while retaining distribution, issue-backend, and artifact settings.

```yaml
schema_version: 2

distribution:
  source: github.com/synthlike/agent-workflows
  version: v0.3.0

installation:
  selected:
    - clarify-intent
  skills:
    clarify-intent: .claude/skills/clarify-intent
    configure-project: .claude/skills/configure-project

issue_tracker:
  backend: local-markdown
  root: .project

artifacts:
  domain: {enabled: true, path: docs/domain}
  arps: {enabled: true, path: docs/decisions, prefix: ARP}
  rfcs: {enabled: true, path: docs/rfcs, prefix: RFC}
  meetings: {enabled: false, path: docs/meetings}
  specifications: {enabled: true, path: docs/specifications}
```

## Installation inventory

- `selected` records user intent, not the calculated dependency set. Names are unique and must exist in the installed release manifest.
- `skills` maps every harness-discovered installed skill to its repository-relative directory.
- Skill paths are unique, remain inside the consumer root, and end with the corresponding skill name.
- The mapped skill set includes `configure-project` and the complete transitive closure of `selected`.
- Additional manifest-known skills may remain installed without silently becoming selected.
- Installer lock files are evidence only and do not replace this inventory.

## Installed lifecycle command

Run the command carried by the installed `configure-project` directory. The exact path depends on the harness-discovered skill location.

Show release identity:

```bash
python3 PATH/TO/configure-project/references/lifecycle.py show-manifest
```

Calculate closure:

```bash
python3 PATH/TO/configure-project/references/lifecycle.py closure clarify-intent
```

Inspect supplied skill directories without reading configuration:

```bash
python3 PATH/TO/configure-project/references/lifecycle.py inspect \
  --consumer-root . \
  --skills-root .claude/skills
```

Verify the complete schema-2 consumer:

```bash
python3 PATH/TO/configure-project/references/lifecycle.py verify-consumer \
  --consumer-root . \
  --skills-root .claude/skills
```

Use repeated `--skill-dir` arguments when discovery spans several parent directories. Every read-only operation supports canonical JSON through `--json` where machine-readable output is relevant.

Verification checks configuration identity and inventory, closure, every distributed file hash, internal links, repository-contained paths, backend and agent guidance, and exact supplied harness discovery. It reports missing, extra, and modified files without changing them.

Schema 2 is the only supported consumer configuration. Installed lifecycle verification rejects every other schema.
