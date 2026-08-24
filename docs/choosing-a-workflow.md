# Choosing a workflow

| Situation | Skill |
| --- | --- |
| An agreed technical stack needs production-compatible foundations | `establish-technical-baseline` |
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
| An incoming report is not yet actionable | `triage-issue` |
| Unexpected behavior needs a supported diagnosis | `investigate-failure` |
| A confirmed defect needs a durable failing check | `capture-regression` |
| Actual implementation needs conformance review | `review-implementation` |
| An initiative is ending or changing direction | `close-initiative` |

## Common flows

### New technical project

```text
establish-technical-baseline -> focused RFCs and ARPs as needed
```

The stack is an input. Product behavior and domain architecture wait for stakeholder evidence.

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

### Defect feedback

```text
triage-issue -> investigate-failure -> capture-regression -> implementation -> review-implementation
```

Investigation diagnoses without fixing. Regression capture changes tests without changing production behavior. Review reports conformance without silently repairing the implementation.

### Initiative outcome

```text
review-implementation -> close-initiative
```

Closure verifies delivered outcomes and records achieved, partial, or abandoned results.

### Stakeholder discussion

```text
prepare-questionnaire -> capture-meeting
```

Afterward, promote requirements, ambiguities, decisions, and actions to their canonical artifacts.
