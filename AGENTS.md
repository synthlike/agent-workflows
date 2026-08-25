# Agent Workflows contributor guide

This repository contains reusable Agent Skills. Keep every workflow independent of any particular application, programming language, issue tracker, documentation generator, or agent harness.

## Design rules

- Skill names use lowercase verb-object form.
- A skill describes semantic operations; backend documents describe concrete tools and storage.
- Use relative links from `SKILL.md` to its references.
- Do not hardcode consumer paths or provider identifiers. Read `.agents/workflows.yaml`, then follow `docs/agents/records.md` for semantic record operations.
- Keep `AGENTS.md` pointers short. Put detailed instructions in skills or referenced documentation.
- Meeting notes, research, prototypes, and planning maps are supporting evidence, not authoritative requirements or decisions.
- RFCs hold unresolved design discussion. ARPs record consequential technical decisions. Specifications describe agreed behavior. Issues track executable work.
- Optional artifact directories are created lazily.

## Verification

Run `scripts/verify.sh` after changing skills or references.

## Engineering workflows

Workflow configuration is in `.agents/workflows.yaml`. Before significant design or planning work, read `docs/agents/workflows.md`. Perform record operations according to `docs/agents/records.md`.
