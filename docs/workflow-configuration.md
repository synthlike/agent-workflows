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

A Bear backend instance requires an absolute executable and project workspace tag. Non-issue destinations use workspace-relative tags:

```yaml
backends:
  notes:
    type: bear
    command: /Applications/Bear.app/Contents/MacOS/bearcli
    workspace: agent-workflows/project-key

records:
  specs:
    enabled: true
    backend: notes
    destination: {tag: specs}
```

Before approval, `configure-workflows` launches `COMMAND mcp-server --only-tags WORKSPACE` for read-only identity, scope, and required-tool preflight. It never creates an MCP registration, note, or tag during preflight. Installed verification accepts a Bear route only after provider preflight succeeds and the immutable adapter declaration contains its non-issue record type and every common operation. Bear never supports `issues`. See the [complete Bear-plus-local example](../examples/bear-local/workflows.yaml) and [Bear operations, recovery, and optional smoke guidance](../backends/record-store/bear.md).

The canonical key is `specs`; the semantic artifact and workflow remain “specification” and `author-specification`. Local paths must remain inside the consumer root. ARP and RFC routes require prefixes. Disabled routes prohibit persistence without approval but retain their destinations and may still permit approved temporary or external output.

A profile question may simplify the interview, but `configure-workflows` expands it into all twelve reviewed routes. It prefers existing conventions before these defaults and does not move, copy, rename, or rewrite existing records.

Canonical templates under `configure-workflows/references/templates/` and the pure `references/templates.py` renderer define exact output. Mapping order does not affect rendered bytes. The renderer replaces only its marked root-guidance section, preserves all unrelated bytes in `AGENTS.md` or the selected equivalent root file, and returns backend assets only for types used by routes.

Schema-3 consumers generate:

- `docs/agents/records.md` with routes, operations, references, revisions, and approval boundaries;
- `docs/agents/workflows.md` with authority and documentation policy;
- `docs/agents/backends/contract.py`, shared by generated helpers;
- `docs/agents/backends/local-markdown.md` and `local-markdown.py` only when a route uses local Markdown;
- `docs/agents/backends/github.md` and `github.py` only when a route uses GitHub; and
- `docs/agents/backends/bear.md` and `bear.py` only when a route uses Bear.

Schema 3 does not generate provider-specific issue-tracker guidance outside `docs/agents/backends/`. Generated backend assets must exactly match the installed `configure-workflows` copies. Record directories remain lazy and are created only on the first approved write.

## Installation inventory

- `selected` records user intent, not the calculated dependency set. Names are unique and must exist in the installed distribution manifest.
- `skills` maps every harness-discovered installed skill to its consumer-root-relative directory.
- Skill paths are unique, remain inside the consumer root, and end with the corresponding skill name.
- The mapped skill set includes `configure-workflows` and the complete transitive closure of `selected`.
- Additional manifest-known skills may remain installed without silently becoming selected.
- Installer lock files are evidence only and do not replace this inventory.
- Manifest `model_invocation` distinguishes model-invocable skills from manual-invocation skills. Both remain installed and discovered when their directories pass integrity checks; prompt visibility is not an inventory requirement.

## Installed lifecycle command

Run the command carried by the installed `configure-workflows` directory. The exact path depends on the harness-discovered skill location.

```bash
python3 PATH/TO/configure-workflows/references/lifecycle.py show-manifest
python3 PATH/TO/configure-workflows/references/lifecycle.py closure clarify-intent
python3 PATH/TO/configure-workflows/references/lifecycle.py inspect \
  --consumer-root . --skills-root .claude/skills
python3 PATH/TO/configure-workflows/references/lifecycle.py verify-consumer \
  --consumer-root . --skills-root .claude/skills
python3 PATH/TO/configure-workflows/references/lifecycle.py plan-consumer \
  --consumer-root . --skills-root .agents/skills \
  --answers /tmp/consumer-answers.json > /tmp/consumer-plan.json
python3 PATH/TO/configure-workflows/references/lifecycle.py apply-consumer \
  --consumer-root . --plan /tmp/consumer-plan.json \
  --expected-digest sha256:REVIEWED_PLAN_DIGEST
```

Use repeated `--skill-dir` arguments when discovery spans several parent directories. Read-only operations support canonical JSON through `--json` where relevant.

`configure-workflows` performs provider-neutral inspection first, asks one project/profile sequence for only unresolved intent, and conditionally gathers provider evidence. It presents one complete plan and requests one approval for that exact local-file digest. It does not compose or repair generated files manually. GitHub label provisioning remains a separate approval, and Bear preflight remains read-only.

`plan-consumer` accepts the strict versioned `references/consumer-answers.schema.json` contract. Answers select explicit workflows or `all`, describe the project and documentation style, name backend instances, select the `local-default` profile, provide per-route overrides, choose the root guidance file, and bind the expected prior state of every managed target. The command writes nothing and emits one canonical JSON plan to stdout.

The plan contains the exact consumer root, immutable distribution identity and manifest hash, normalized selected workflows and closure, complete installed inventory, exact UTF-8 text, copied-asset source and destination hashes, every target's expected prior state, directories needed for managed files, and lazy record destinations deliberately left absent. Its `digest` is `sha256` over canonical plan JSON excluding only `digest`. Identical state and answers produce identical bytes. A stale prior hash, malformed answer, unsupported route/backend combination, escaping path, collision, incomplete installation, or altered bundled asset stops planning without a consumer write. Provider preflight evidence is gathered conditionally by the workflow; local file planning never invokes provider tools.

`apply-consumer` requires the exact reviewed plan file and digest. It accepts only canonical plan bytes, rechecks release identity, the plan-bound consumer root and complete installed inventory, canonical rendering and target set, all prior target and bundled-source hashes, destination containment, directory intent, and operation shape before consumer mutation. It stages every output on the destination filesystem, atomically replaces only changed planned targets, runs installed `verify-consumer`, and confirms lazy record destinations remain absent. On a caught write or verification failure, it restores prior target files and removes newly created planned directories when safe, reporting whether rollback succeeded. Replanning already-applied identical intent yields unchanged targets and a no-op apply.

Apply never writes a skill directory, record destination, backend record, or provider configuration. GitHub label provisioning remains a separately reviewed and approved external operation.

Verification checks configuration shape, identity, inventory, closure, distributed file hashes, internal links, consumer-root containment, generated guidance, and exact backend assets. Schema 3 rejects missing and unknown routes, fields, backend instances, unsupported backend contracts, malformed destinations, escaping paths, stale helpers, and obsolete issue guidance. A routed backend must declare the record type and its complete operation set before any backend write: common record operations for non-issue routes or every issue-extension operation for `issues`. Capability declarations belong to distributed adapters; project configuration cannot override them.

Schema-2 keys such as `issue_tracker`, `artifacts`, and `specifications` have no compatibility aliases. Configuration changes do not move, copy, relabel, or rewrite existing records. Existing content remains where it was until separately approved record work handles it.
