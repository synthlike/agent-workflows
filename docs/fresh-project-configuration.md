# Fresh-project configuration

The recommended fresh setup installs the complete Agent Workflows skill set. The distribution is small, every dependency is already available, and project configuration can still select only the workflows the user intends to use. A complete installation does not need a release bundle during normal setup.

Human intent and approval remain in `configure-project`. Its installed lifecycle command performs deterministic inspection and verification.

## 1. Install and discover all skills

Use an Agent Skills-compatible installer or intact manual copy. For example:

```bash
npx skills@latest add synthlike/agent-workflows \
  --skill '*' \
  --copy
```

The installer may ask which harness should discover the skills. Ask the harness for every exact discovered directory and confirm that `configure-project` is present. Preserve each skill directory intact and do not replace an existing directory.

## 2. Select, configure, and confirm

Invoke `configure-project` from the consumer Git root. Tell it which workflows you explicitly selected even though all skills are installed. It records selected intent separately from the complete harness-discovered inventory and verifies dependency closure.

Review the proposed schema-2 `.agents/workflows.yaml`, backend guidance, workflow guidance, and concise agent pointer. Nothing is written before approval. Optional artifact and issue directories remain absent.

Ask the harness to rediscover the installed skills after any approved change. Do not write final configuration until it confirms the expected paths.

## 3. Verify and commit

Run the installed verifier against the exact discovered directories. For a common single-root installation:

```bash
python3 PATH/TO/configure-project/references/lifecycle.py verify-consumer \
  --consumer-root . \
  --skills-root .claude/skills
```

Use repeated `--skill-dir` arguments instead when discovery spans several parent directories. Commit the reviewed skill directories, configuration, and guidance before creating project artifacts.

## Advanced: selective installation from a release bundle

A consumer may initially install only `configure-project` and explicitly selected workflows. In that case, `configure-project` calculates the missing dependency closure and uses the matching verified release bundle as its source. This path is useful for selective, offline, or exactly reproducible installation.

### 1. Generate the dry run

From the consumer root, invoke the lifecycle command carried by discovered `configure-project`:

```bash
python3 PATH/TO/configure-project/references/lifecycle.py plan-fresh \
  /path/to/agent-workflows-vMAJOR.MINOR.PATCH.tar.gz \
  --consumer-root . \
  --skills-root .claude/skills \
  --selected develop-rfc \
  --output /tmp/agent-workflows-plan.json
```

Use repeated `--skill-dir` arguments when discovery spans several parent directories. Repeat `--selected` for each workflow explicitly chosen by the user.

The default destination for every missing dependency is beside the discovered `configure-project`. Override an individual destination when needed:

```bash
--destination research-question=.agents/skills/research-question
```

Overrides must remain inside the consumer repository, end with the skill name, and name an absent path.

The plan identifies:

- release identity and complete bundle SHA-256;
- selected workflows and calculated closure;
- discovered, unexpected, and missing skills;
- each source, destination, file set, and create action;
- the schema-2 distribution and installation inventory fragment;
- configuration and guidance files that `configure-project` will propose; and
- blocking integrity or destination conflicts.

Planning is read-only except for the explicitly requested plan output. Existing incomplete, modified, duplicate, unknown, or occupied skill directories block apply.

### 2. Review and apply

After reviewing and approving the complete dry run, apply the exact plan with the same release bundle:

```bash
python3 PATH/TO/configure-project/references/lifecycle.py apply-fresh \
  /path/to/agent-workflows-vMAJOR.MINOR.PATCH.tar.gz \
  --consumer-root . \
  --plan /tmp/agent-workflows-plan.json
```

Apply revalidates the bundle, installed skills, selected intent, destinations, and plan identity. It stages complete missing skill directories beside their destinations and atomically publishes only absent directories. It never replaces or removes an existing skill or writes project configuration and guidance.

If apply fails, it removes unpublished staging directories and reports every published skill directory requiring cleanup. General rollback is not part of the fresh-project flow.

After apply, return to the common discovery, configuration, verification, and commit steps above.

## Maintainer smoke test

The opt-in smoke test exercises the advanced selective path with the real `skills@latest` installer and Pi discovery against a temporary Git repository:

```bash
scripts/smoke-fresh-install.sh
```

It intentionally installs only `configure-project` and `frame-product-problem`, builds and applies the missing closure, confirms Pi discovery through its SDK resource loader, writes schema-2 setup, verifies from copied lifecycle assets with no source checkout, checks lazy directories, and removes the temporary repository.

The regular unit and fixture suite covers complete and selective inventory, destination override, several discovered roots, occupied destinations, changed plan inputs, staging and publication failures, and existing-project preservation without requiring network access.
