# Distribution manifest

Each release publishes a deterministic JSON manifest at `skills/configure-workflows/references/distribution-manifest.json`. The installed `configure-workflows` skill carries this manifest and the lifecycle command that validates it.

The manifest has this shape:

```json
{
  "manifest_version": 1,
  "distribution": {
    "source": "github.com/example/agent-workflows",
    "version": "vMAJOR.MINOR.PATCH"
  },
  "configuration": {
    "current_schema": 2,
    "readable_schemas": [2]
  },
  "skills": {
    "configure-workflows": {
      "dependencies": [],
      "files": {
        "SKILL.md": "<sha256>"
      }
    }
  }
}
```

- `distribution.source` identifies the canonical distribution.
- `distribution.version` is an exact semantic release identifier.
- `configuration` declares the only configuration schema accepted by the installed verifier.
- `skills` contains every distributed skill.
- `dependencies` is the sorted, unique list of additional direct dependencies. `configure-workflows` is required implicitly and is not repeated in each list.
- `files` maps every distributed file inside the skill directory to its lowercase SHA-256 digest.
- `configure-workflows/references/distribution-manifest.json` is excluded from its own file map.

A supported consumer installs the complete skill inventory. `.agents/workflows.yaml` separately records which workflows the user explicitly selected and the exact consumer-root-relative path of every harness-discovered skill. Installed verification compares those paths and files with the embedded manifest and does not require a source checkout.

## Maintainer commands

Regenerate the manifest after changing distributed skills or release metadata:

```bash
python3 skills/configure-workflows/references/lifecycle.py generate-release
```

Verify the committed manifest:

```bash
python3 skills/configure-workflows/references/lifecycle.py check-release
```

Repository verification also checks dependency declarations, source inventory, canonical JSON, file hashes, and consumer installation:

```bash
scripts/verify.sh
```
