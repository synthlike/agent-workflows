---
id: ISSUE-0052
title: "Bundle canonical consumer guidance templates"
kind: "implementation"
status: resolved
created: 2026-08-25
assignee: "pi"
parent: "ISSUE-0050-streamline-deterministic-consumer-configuration.md"
blocked_by:
labels: ["lifecycle","configuration"]
---
# Bundle canonical consumer guidance templates

## Parent

Streamline deterministic consumer configuration

## What to build

Provide canonical distribution-managed templates that make configuration and guidance generation deterministic while preserving explicit project-owned content boundaries.

## Acceptance criteria

- [ ] Bundled templates cover schema-3 `workflows.yaml`, `docs/agents/workflows.md`, `docs/agents/records.md`, and the root agent-guidance section.
- [ ] Workflow guidance always contains the literal canonical instruction to read `docs/agents/records.md` for record routing and operations.
- [ ] Templates render every route explicitly, include exact used backend assets, preserve authority/documentation policy, and describe disabled-route and approval boundaries.
- [ ] Rendering is byte-for-byte deterministic for identical normalized inputs.
- [ ] Root guidance uses an unambiguous managed section and preserves all unrelated existing `AGENTS.md` or equivalent bytes.
- [ ] Generated template output passes installed `verify-consumer` without hand repair.
- [ ] Release manifest integrity covers every template.

## Blocked by

None.

## Out of scope

Applying generated files, replacing skill directories, provider provisioning, and record migration.

## Comments
## Resolution

Bundled canonical templates for schema-3 `.agents/workflows.yaml`, `docs/agents/workflows.md`, `docs/agents/records.md`, and the marked root agent-guidance section. Added a pure renderer that accepts normalized distribution, installation, backend, route, documentation-policy, and root-guidance inputs; emits every route explicitly in canonical order; returns only the shared contract and guidance/helper pairs for backend types actually used; and performs no consumer writes. It normalizes mapping order for byte-identical output, preserves unrelated bytes in `AGENTS.md` or an equivalent selected root file, rejects ambiguous managed markers, and supports idempotent managed-section replacement. Workflow guidance includes the literal instruction to read `docs/agents/records.md`; templates preserve semantic authority, documentation policy, lazy destination behavior, disabled-route boundaries, and mutation approval requirements. Replaced the unmarked legacy root seed with the canonical managed template and marked this repository's own managed section without changing unrelated guidance. Added all-local and mixed-backend rendering regressions, byte determinism and preservation checks, exact-asset checks, and an end-to-end generated-output test that passes installed `verify-consumer` without repair. Manifest format 2 covers the renderer and every template. `scripts/verify.sh` passes with 144 tests.
