# Verifying a consumer installation

## Installed verification

A consumer verifies itself with the lifecycle command carried by its installed `configure-workflows` skill. Pass the consumer root plus the exact skill directories discovered by its harness:

```bash
python3 PATH/TO/configure-workflows/references/lifecycle.py verify-consumer \
  --consumer-root /path/to/consumer \
  --skills-root /path/to/discoverable/skills
```

Use repeated `--skill-dir` arguments when the harness supplies exact skills from several roots. `--skills-root` recursively inspects skill directories under one discovery root. Add `--json` for deterministic machine-readable output. See [Workflow configuration](workflow-configuration.md) for the inventory contract.

`inspect` distinguishes `installed`, `model_invocable`, and `manual_invocation`. These sets come from integrity-checked directories and immutable manifest policy. They do not claim what a running model actually received in its startup prompt. For Pi, manual-invocation skills may be absent from that prompt while remaining available through `/skill:name`.

## Checks

Verification fails when:

- `configure-workflows` or a direct dependency of an installed skill is absent;
- a skill directory lacks `SKILL.md`, its frontmatter name differs from its directory, or an internal relative reference is broken or escapes the skill directory;
- an installed skill differs from the corresponding unmodified distribution skill, surfacing locally added, missing, or modified files before an update;
- root `.agents/workflows.yaml` is missing or another nested configuration exists;
- configuration schema, immutable distribution identity, named record backends, explicit GitHub repository/login or Bear command/workspace, matching generated backend assets, complete record routes, consumer-root-contained paths, or required guidance are invalid; or
- root agent guidance does not point to workflow and record-routing guidance.

The verifier compares every installed file and dependency with the manifest embedded in the installed `configure-workflows` directory. It does not require a distribution source checkout.

Harness-specific runtime prompt state remains outside the lifecycle command. For Pi, a complete integrity-checked project `.agents/skills/` root that existed at startup is sufficient discovery evidence; restart or rediscover only after post-startup installation or when a manual command is unavailable. Other harnesses supply their supported discovery roots or exact directories.
