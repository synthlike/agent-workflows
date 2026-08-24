# Release manifest and bundle

Each release publishes a deterministic JSON manifest at `skills/configure-project/references/distribution-manifest.json`. The installed `configure-project` skill carries this manifest and the lifecycle command that validates it.

`release/metadata.json` declares the exact release identity, configuration compatibility, and skill inventory. Skill-to-skill routing declared by exact skill names in `SKILL.md` inline code is the authoritative dependency source. The JSON manifest is generated from those sources, and the [human-readable dependency table](workflow-dependencies.md) is verified against the same declarations.

## Manifest schema version 1

```json
{
  "manifest_version": 1,
  "distribution": {
    "source": "github.com/OWNER/agent-workflows",
    "version": "v0.3.0"
  },
  "configuration": {
    "current_schema": 2,
    "readable_schemas": [1, 2]
  },
  "skills": {
    "configure-project": {
      "dependencies": [],
      "files": {
        "SKILL.md": "64 lowercase hexadecimal SHA-256 characters"
      }
    }
  }
}
```

Rules:

- `manifest_version` identifies this JSON contract independently of consumer configuration schemas.
- Distribution `version` is an exact `vMAJOR.MINOR.PATCH` release.
- `current_schema` is included exactly once in sorted, unique `readable_schemas`.
- `skills` contains every distributed skill exactly once.
- `dependencies` is the sorted, unique list of additional direct dependencies. `configure-project` is required implicitly for every installation and is not repeated in each list.
- `files` contains every regular distributed file under that skill, keyed by normalized skill-relative POSIX path.
- Every digest is lowercase SHA-256 over exact file bytes.
- The manifest excludes itself to avoid a recursive digest.
- Source generation rejects symlinks and non-regular files. Caches, bytecode, and OS metadata are excluded rather than distributed.
- Installer locks and links outside skill directories, consumer configuration and guidance, backend state, and project artifacts are outside the manifest boundary.

The canonical JSON encoding uses UTF-8, sorted object keys, two-space indentation, and one trailing newline.

## Release bundle

The canonical release asset is `agent-workflows-vMAJOR.MINOR.PATCH.tar.gz`. It contains regular files only under one root named `agent-workflows-vMAJOR.MINOR.PATCH/`:

```text
agent-workflows-v0.3.0/
├── CHANGELOG.md
└── skills/
    ├── configure-project/
    │   ├── SKILL.md
    │   └── references/
    │       ├── distribution-manifest.json
    │       └── lifecycle.py
    └── ...
```

Archive generation normalizes file order, timestamps, ownership, names, and permissions. Validation computes SHA-256 over the complete compressed bytes before safe extraction, validates the embedded manifest, rejects unsafe or unexpected members, and verifies every listed skill file.

The lifecycle command accepts local files or HTTPS URLs:

```bash
python3 skills/configure-project/references/lifecycle.py validate-bundle \
  agent-workflows-v0.3.0.tar.gz
```

To stage validated files without using `tar` extraction:

```bash
python3 skills/configure-project/references/lifecycle.py validate-bundle \
  agent-workflows-v0.3.0.tar.gz \
  --stage /temporary/empty/directory
```

## Source release operations

Update `release/metadata.json` when release identity, supported schemas, or the skill inventory changes. Regenerate the committed manifest after changing release metadata or a skill:

```bash
python3 skills/configure-project/references/lifecycle.py generate-release
```

Verify the manifest and deterministic in-memory bundle:

```bash
python3 skills/configure-project/references/lifecycle.py check-release
```

Build the release asset:

```bash
python3 skills/configure-project/references/lifecycle.py build-bundle \
  --output dist/agent-workflows-v0.3.0.tar.gz
```
