# Fresh-project configuration

A supported fresh setup installs the complete Agent Workflows skill set. The distribution is small, every dependency is available, and project configuration can still select only the workflows the user intends to use.

Human intent and approval remain in `configure-project`. Its installed lifecycle command performs deterministic inspection and verification. It never installs or changes skill directories.

## 1. Install and discover all skills

Use an Agent Skills-compatible installer or intact manual copy. For example:

```bash
npx skills@latest add synthlike/agent-workflows \
  --skill '*' \
  --copy
```

The installer may ask which harness should discover the skills. Ask the harness for every exact discovered directory and confirm that all distributed skills are present. Preserve each skill directory intact and do not replace an existing directory.

If inspection reports an absent, unexpected, duplicate, incomplete, or modified skill, stop configuration. Correct the installation through the external installer or a reviewed intact manual copy, ask the harness to rediscover skills, and inspect again.

## 2. Select, configure, and confirm

Invoke `configure-project` from the consumer Git root. Tell it which workflows you explicitly selected even though all skills are installed. It records selected intent separately from the complete harness-discovered inventory and verifies dependency closure.

Review the proposed schema-2 `.agents/workflows.yaml`, backend guidance, workflow guidance, and concise agent pointer. Nothing is written before approval. Optional artifact and issue directories remain absent.

## 3. Verify and commit

Run the installed verifier against the exact discovered directories. For a common single-root installation:

```bash
python3 PATH/TO/configure-project/references/lifecycle.py verify-consumer \
  --consumer-root . \
  --skills-root .claude/skills
```

Use repeated `--skill-dir` arguments instead when discovery spans several parent directories. Commit the reviewed skill directories, configuration, and guidance before creating project artifacts.

## Maintainer smoke test

The opt-in smoke test exercises complete installation with the real `skills@latest` installer and Pi discovery against a temporary Git repository:

```bash
scripts/smoke-fresh-install.sh
```

It installs all skills, confirms Pi discovery through its SDK resource loader, writes schema-2 setup with one explicitly selected workflow, verifies from copied lifecycle assets with no source checkout, checks lazy directories, and removes the temporary repository.

The regular unit and fixture suite covers complete inventory, several discovered roots, missing and modified skills, configuration validation, and existing-project preservation without requiring network access.
