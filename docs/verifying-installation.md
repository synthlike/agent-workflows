# Verifying a consumer installation

## v0.2 installed verification

A schema-2 consumer verifies itself with the lifecycle command carried by its installed `configure-project` skill. Pass the consumer root plus the exact skill directories discovered by its harness:

```bash
python3 PATH/TO/configure-project/references/lifecycle.py verify-consumer \
  --consumer-root /path/to/consumer \
  --skills-root /path/to/discoverable/skills
```

Use repeated `--skill-dir` arguments when the harness discovers skills from several parents. Add `--json` for deterministic machine-readable output. See [Workflow configuration schema 2](workflow-configuration.md) for the inventory contract.

## Schema-1 migration verification

Until the known v0.1.0 installation migrates, source-checkout verification remains available. Run it from the Agent Workflows distribution and pass the consumer repository root plus the skill directories discovered by its agent harness.

When discoverable skills share a parent directory:

```bash
python3 scripts/verify_consumer_installation.py \
  --consumer-root /path/to/consumer \
  --skills-root /path/to/discoverable/skills
```

When a harness discovers skills from several locations, pass each directory explicitly:

```bash
python3 scripts/verify_consumer_installation.py \
  --consumer-root /path/to/consumer \
  --skill-dir /first/location/configure-project \
  --skill-dir /another/location/clarify-intent
```

The physical skill location is not part of the contract. The verifier checks the set supplied through `--skills-root` or `--skill-dir`.

## Checks

Verification fails when:

- `configure-project` or a direct dependency of an installed skill is absent;
- a skill directory lacks `SKILL.md`, its frontmatter name differs from its directory, or an internal relative reference is broken or escapes the skill directory;
- an installed skill differs from the corresponding unmodified distribution skill, surfacing locally added, missing, or modified files before an update;
- root `.agents/workflows.yaml` is missing or another nested configuration exists;
- configuration schema, immutable distribution identity, issue backend, artifact settings, repository-contained paths, or required guidance are invalid; or
- root agent guidance does not point to workflow and issue-backend guidance.

By default, the verifier compares against `skills/` and `docs/workflow-dependencies.md` beside the verification script. Use `--source-skills` or `--dependency-table` to verify a copied release from another location.

Harness-specific discovery itself remains outside this script: the harness or installer supplies the exact directories it discovered.
