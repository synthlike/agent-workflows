# Customizing

Project policy overrides toolkit defaults. Prefer changing `.agents/workflows.yaml` and project documentation over editing installed skills.

`frame-product-problem` prefers an existing product or discovery documentation location and asks before creating another. Its brief is supporting evidence; projects may customize interview, consent, evidence, and retention conventions without promoting founder belief into agreed behavior.

`establish-technical-baseline` prefers an existing engineering or architecture documentation location and asks before creating another. Its baseline is a project-owned supporting index; customize its routine conventions there while keeping consequential decisions in ARPs and agreed behavior in specifications.

`configure-workflows` adds a `## Documentation style` section to `docs/agents/workflows.md`. For a fresh project, it defaults to direct plain language: active voice, short sentences, explicit references, established domain terms, and one action per procedural step, without idioms, unnecessary synonyms, or ambiguous pronouns. This is guidance inspired by controlled-language practices, not a claim of ASD-STE100 compliance. Replace or extend the section when the project has its own writing standard.

Edit a skill only when the workflow itself differs. A local skill edit becomes consumer-owned: record it and reconcile it explicitly during updates so it is never overwritten silently. See [Updating](updating.md).

New record backends must implement every operation in [`backends/record-store/contract.md`](../backends/record-store/contract.md), plus the complete issue extension before accepting the `issues` route. Executable backend helpers keep a canonical implementation under `backends/record-store/` and an exact bundled copy under `skills/configure-workflows/references/backends/record-store/` so configured consumers receive the helper. New skills should use lowercase verb-object names and keep implementation details in references where possible.
