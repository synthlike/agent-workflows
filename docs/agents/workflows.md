# Engineering workflows

Canonical configuration is in [`.agents/workflows.yaml`](../../.agents/workflows.yaml). Issue operations follow the [local-Markdown backend](issue-tracker.md).

## Distribution

- Source: `github.com/synthlike/agent-workflows`
- Version: `v0.3.0`
- Configuration schema: `2`

## Installation inventory

All 19 current workflows are explicitly selected. The complete 20-skill closure, including mandatory `configure-project`, is discovered under `skills/<skill-name>`.

## Artifact authority

| Information | Canonical artifact |
| --- | --- |
| Domain terminology and boundaries | Domain model |
| Unresolved technical or design discussion | RFC |
| Accepted consequential technical decision | ARP |
| Agreed product or system behavior | Specification |
| Executable work | Issue tracker |
| What happened in a meeting | Meeting notes |
| Current system behavior | Code and tests |

Supporting research, prototypes, questionnaires, meetings, and planning maps are evidence rather than authoritative requirements or decisions.

## Configured paths

| Capability | State | Path |
| --- | --- | --- |
| Domain documentation | Enabled | `docs/domain/` |
| ARPs | Enabled | `docs/decisions/` (`ARP` prefix) |
| RFCs | Enabled | `docs/rfcs/` (`RFC` prefix) |
| Specifications | Enabled | `docs/specifications/` |
| Meeting notes | Disabled | `docs/meetings/` when enabled |
| Local issues | Enabled | `.project/` |

Create optional artifact and local-issue directories only when writing their first artifact. Ask before enabling a disabled capability. Do not migrate existing artifacts as a side effect of configuration or installation.
