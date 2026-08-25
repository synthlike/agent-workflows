# Workflow configuration schema 2

`.agents/workflows.yaml` is the single canonical configuration at the consumer Git root. Schema 2 records installation intent and discovered paths while retaining distribution, issue-backend, and artifact settings.

```yaml
schema_version: 2

distribution:
  source: github.com/synthlike/agent-workflows
  version: vMAJOR.MINOR.PATCH

installation:
  selected:
    - clarify-intent
  skills:
    clarify-intent: .claude/skills/clarify-intent
    configure-workflows: .claude/skills/configure-workflows

issue_tracker:
  backend: local-markdown
  root: .project

artifacts:
  domain: {enabled: true, path: docs/domain}
  arps: {enabled: true, path: docs/decisions, prefix: ARP}
  rfcs: {enabled: true, path: docs/rfcs, prefix: RFC}
  meetings: {enabled: false, path: docs/meetings}
  research: {enabled: true, path: docs/research}
  questionnaires: {enabled: true, path: docs/questionnaires}
  technical_baselines: {enabled: true, path: docs/engineering}
  prototypes: {enabled: false, path: docs/prototypes}
  handoffs: {enabled: false, path: .agents/handoffs}
  specifications: {enabled: true, path: docs/specifications}
```

Each artifact capability has an `enabled` retention policy and a repository-contained `path`. Disabled capabilities prohibit repository writes without approval but may still produce temporary or external output. Fresh projects enable research, questionnaires, and technical baselines; they disable retained prototypes, durable handoffs, and meeting notes by default. `configure-workflows` adjusts these recommendations to the project's nature, collaboration model, repository evidence, and existing conventions.

Supported `issue_tracker.backend` values are `local-markdown` and `github`. Local Markdown requires a repository-contained `root`. GitHub requires an explicit account identity, matching backend guidance, and the generated helper:

```yaml
issue_tracker:
  backend: github
  login: octocat
```

`configure-workflows` lists authenticated account names and asks which login to record. It never assumes that the currently active account is intended and never changes global `gh` authentication silently. Every helper invocation verifies that the configured login is authenticated and active before repository access. Runtime preflight also verifies GitHub Cloud, enabled Issues, and repository write access.

## Installation inventory

- `selected` records user intent, not the calculated dependency set. Names are unique and must exist in the installed distribution manifest.
- `skills` maps every harness-discovered installed skill to its repository-relative directory.
- Skill paths are unique, remain inside the consumer root, and end with the corresponding skill name.
- The mapped skill set includes `configure-workflows` and the complete transitive closure of `selected`.
- Additional manifest-known skills may remain installed without silently becoming selected.
- Installer lock files are evidence only and do not replace this inventory.

## Installed lifecycle command

Run the command carried by the installed `configure-workflows` directory. The exact path depends on the harness-discovered skill location.

Show release identity:

```bash
python3 PATH/TO/configure-workflows/references/lifecycle.py show-manifest
```

Calculate closure:

```bash
python3 PATH/TO/configure-workflows/references/lifecycle.py closure clarify-intent
```

Inspect supplied skill directories without reading configuration:

```bash
python3 PATH/TO/configure-workflows/references/lifecycle.py inspect \
  --consumer-root . \
  --skills-root .claude/skills
```

Verify the complete schema-2 consumer:

```bash
python3 PATH/TO/configure-workflows/references/lifecycle.py verify-consumer \
  --consumer-root . \
  --skills-root .claude/skills
```

Use repeated `--skill-dir` arguments when discovery spans several parent directories. Every read-only operation supports canonical JSON through `--json` where machine-readable output is relevant.

Verification checks configuration identity and inventory, closure, every distributed file hash, internal links, repository-contained paths, backend and agent guidance, and exact supplied harness discovery. It reports missing, extra, and modified files without changing them.

Schema 2 is the only supported consumer configuration. Installed lifecycle verification rejects every other schema.
