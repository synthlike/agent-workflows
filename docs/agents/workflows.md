# Engineering workflows

Canonical configuration is in [`.agents/workflows.yaml`](../../.agents/workflows.yaml).

Read `docs/agents/records.md` for record routing and operations.

## Distribution

- Source: `github.com/synthlike/agent-workflows`
- Version: `v0.5.0`
- Configuration schema: `3`

## Installation inventory

All 19 current workflows are explicitly selected. The complete 20-skill closure, including mandatory `configure-workflows`, is discovered under `skills/<skill-name>`.

## Artifact authority

| Information | Canonical artifact |
| --- | --- |
| Domain terminology and boundaries | Domain model |
| Unresolved technical or design discussion | RFC |
| Accepted consequential technical decision | ARP |
| Agreed product or system behavior | Specification |
| Executable work | Issue |
| What happened in a meeting | Meeting notes |
| Current system behavior | Code and tests |

Supporting research, prototypes, questionnaires, meetings, and planning maps are evidence rather than authoritative requirements or decisions. Authority derives from semantic record type, not storage backend.

## Documentation style

Write clear, direct documentation. Prefer active voice, short sentences, explicit references, and established domain terms. Avoid idioms, unnecessary synonyms, and ambiguous pronouns. Use one action per procedural step.

Create local destinations only on their first approved record write. Ask before persisting through a disabled route. Do not migrate existing records as a side effect of configuration, installation, or route changes.
