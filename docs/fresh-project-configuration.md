# Fresh-project configuration

A v0.3 fresh installation needs `configure-project` and the workflows the user explicitly selects. It may initially omit transitive dependencies; `configure-project` calculates and adds the missing closure from the matching verified release bundle.

Human intent and approval remain in the skill. The installed lifecycle command performs deterministic inspection, planning, bundle validation, and non-destructive skill creation.

## 1. Install and discover an initial selection

Use an Agent Skills-compatible installer or intact manual copy. Ask the harness for the exact directories it discovers. `configure-project` must be among them.

## 2. Generate the dry run

From the consumer root, invoke the lifecycle command carried by discovered `configure-project`:

```bash
python3 PATH/TO/configure-project/references/lifecycle.py plan-fresh \
  /path/to/agent-workflows-v0.3.0.tar.gz \
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

## 3. Review and apply

After reviewing and approving the complete `configure-project` dry run, apply the exact plan with the same release bundle:

```bash
python3 PATH/TO/configure-project/references/lifecycle.py apply-fresh \
  /path/to/agent-workflows-v0.3.0.tar.gz \
  --consumer-root . \
  --plan /tmp/agent-workflows-plan.json
```

Apply revalidates the bundle, installed skills, selected intent, destinations, and plan identity. It stages complete missing skill directories beside their destinations and atomically publishes only absent directories. It never replaces or removes an existing skill or writes project configuration and guidance.

If apply fails, it removes unpublished staging directories and reports every published skill directory requiring cleanup. General rollback is not part of the fresh-project flow.

## 4. Confirm discovery and configure

Ask the harness to rediscover the installed skills. Do not write final configuration until it confirms the complete closure at the planned paths.

`configure-project` then presents and writes the separately approved schema-2 `.agents/workflows.yaml`, backend guidance, workflow guidance, and concise agent pointer. Optional artifact and issue directories remain absent.

## 5. Verify and commit

Run the installed verifier against the exact rediscovered directories:

```bash
python3 PATH/TO/configure-project/references/lifecycle.py verify-consumer \
  --consumer-root . \
  --skills-root .claude/skills
```

Commit the reviewed skill directories, configuration, and guidance before creating project artifacts.

## Maintainer smoke test

The opt-in smoke test exercises the real `skills@latest` installer and Pi discovery against a temporary Git repository:

```bash
scripts/smoke-fresh-install.sh
```

It intentionally installs only `configure-project` and `develop-rfc`, builds and applies the missing closure, confirms Pi discovery through its SDK resource loader, writes schema-2 setup, verifies from copied lifecycle assets with no source checkout, checks lazy directories, and removes the temporary repository.

The regular unit and fixture suite covers destination override, several discovered roots, occupied destinations, changed plan inputs, staging and publication failures, and existing-project preservation without requiring network access.
