# Choosing a workflow

| Situation | Skill |
| --- | --- |
| The request, plan, or decision is unclear | `clarify-intent` |
| Domain terms or boundaries are inconsistent | `model-domain` |
| External facts are missing | `research-question` |
| A concrete artifact would improve a design discussion | `prototype-design` |
| Alternatives require collaborative technical discussion | `develop-rfc` |
| A consequential technical decision has been accepted | `record-arp` |
| A large initiative is too uncertain for one planning session | `plan-initiative` |
| Agreed requirements need a coherent description | `author-specification` |
| Approved work needs executable vertical slices | `plan-implementation` |
| Another stakeholder holds missing information | `prepare-questionnaire` |
| A meeting needs concise minutes and follow-up extraction | `capture-meeting` |
| Another agent or session will continue the work | `prepare-handoff` |

## Common flows

### Small, understood change

```text
clarify-intent -> author-specification -> plan-implementation
```

### Ambiguous design

```text
clarify-intent -> develop-rfc -> record-arp -> author-specification
```

Use `research-question` and `prototype-design` inside RFC development when facts or fidelity are missing.

### Large uncertain initiative

```text
plan-initiative -> author-specification -> plan-implementation
```

The initiative map may invoke clarification, research, prototyping, and RFC development to resolve its decision tickets.

### Stakeholder discussion

```text
prepare-questionnaire -> capture-meeting
```

Afterward, promote requirements, ambiguities, decisions, and actions to their canonical artifacts.
