# Verifying a consumer installation

## Installed verification

A consumer verifies itself with the lifecycle command carried by its installed `configure-workflows` skill. Pass the consumer root plus the exact skill directories discovered by its harness:

```bash
python3 PATH/TO/configure-workflows/references/lifecycle.py verify-consumer \
  --consumer-root /path/to/consumer \
  --skills-root /path/to/discoverable/skills
```

Use repeated `--skill-dir` arguments when the harness discovers skills from several parents. Add `--json` for deterministic machine-readable output. See [Workflow configuration](workflow-configuration.md) for the inventory contract.

## Checks

Verification fails when:

- `configure-workflows` or a direct dependency of an installed skill is absent;
- a skill directory lacks `SKILL.md`, its frontmatter name differs from its directory, or an internal relative reference is broken or escapes the skill directory;
- an installed skill differs from the corresponding unmodified distribution skill, surfacing locally added, missing, or modified files before an update;
- root `.agents/workflows.yaml` is missing or another nested configuration exists;
- configuration schema, immutable distribution identity, supported issue backend, explicit GitHub login, matching backend guidance, required GitHub helper, record routes, consumer-root-contained paths, or required guidance are invalid; or
- root agent guidance does not point to workflow and issue-backend guidance.

The verifier compares every installed file and dependency with the manifest embedded in the installed `configure-workflows` directory. It does not require a distribution source checkout.

Harness-specific discovery remains outside the lifecycle command: the harness or installer supplies the exact directories it discovered.
