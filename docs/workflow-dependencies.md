# Workflow dependencies

This is the release-facing dependency table for v0.1 selective installations.

Every installation must include `configure-project`, the workflows selected by the consumer, and the complete transitive closure of their additional direct dependencies. Dependency cycles are valid. A generic installer may not resolve this table automatically, so the installer or operator must select the resulting closure.

| Skill | Additional direct skill dependencies |
| --- | --- |
| `author-specification` | `develop-rfc` |
| `capture-meeting` | `author-specification`, `develop-rfc`, `model-domain`, `record-arp` |
| `clarify-intent` | None |
| `configure-project` | None |
| `develop-rfc` | `author-specification`, `clarify-intent`, `prototype-design`, `record-arp`, `research-question` |
| `model-domain` | `develop-rfc`, `record-arp` |
| `plan-implementation` | `clarify-intent`, `develop-rfc`, `plan-initiative` |
| `plan-initiative` | `author-specification`, `clarify-intent`, `develop-rfc`, `model-domain`, `plan-implementation`, `prototype-design`, `record-arp`, `research-question` |
| `prepare-handoff` | None |
| `prepare-questionnaire` | None |
| `prototype-design` | None |
| `record-arp` | `develop-rfc` |
| `research-question` | None |

A direct dependency is declared when a `SKILL.md` names another distributed skill in inline code. Cross-skill routing must use that form so verification can keep this table synchronized. Artifact references such as RFCs, ARPs, specifications, issues, research, and prototypes do not create dependencies unless the source skill explicitly names another skill.

To validate the table and print a selection's closure:

```bash
python3 scripts/verify_workflow_dependencies.py develop-rfc
```

The output is the stable, sorted set that must be installed.
