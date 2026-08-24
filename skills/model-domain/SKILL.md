---
name: model-domain
description: Build and sharpen a project's domain vocabulary and context boundaries. Use when terminology is vague, overloaded, contradictory, or newly resolved.
license: MIT
---

# Model Domain

Maintain the project's ubiquitous language while design work happens.

## Locate the model

Read `.agents/workflows.yaml` when present. Follow its configured domain path. Otherwise inspect existing `CONTEXT.md`, glossary, and context-map conventions before proposing a location.

## During discussion

- Challenge terms that conflict with the existing language.
- Propose one canonical name for overloaded concepts.
- Invent concrete edge cases to test boundaries and relationships.
- Check whether code and documentation agree with stated behavior.
- Update the domain model immediately after a term is explicitly resolved.

Use [the context format](references/context-template.md).

The domain model is a glossary, not a specification or decision log. It must not contain implementation choices, meeting history, plans, or general programming terms. Send unresolved designs to `develop-rfc` and accepted consequential technical decisions to `record-arp`.

For multiple bounded contexts, maintain a context map linking each context's glossary and describing their relationships. Do not introduce multiple contexts merely because the repository is a monorepo.
