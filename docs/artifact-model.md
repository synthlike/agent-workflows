# Artifact model

Each kind of information has one canonical home.

| Information | Canonical artifact |
| --- | --- |
| Domain terminology and boundaries | Domain model |
| Unresolved technical or design discussion | RFC |
| Accepted consequential technical decision | ARP |
| Agreed product or system behavior | Specification |
| Executable work | Issue tracker |
| What happened in a meeting | Meeting notes |
| Current system behavior | Code and tests |

## Authority

Supporting artifacts are evidence, not authority. Research establishes facts. Prototypes make choices concrete. Questionnaires and meetings collect stakeholder input. Initiative maps organize unresolved decisions. Promote their outcomes instead of treating them as permanent specifications.

- New ambiguity becomes an RFC.
- A consequential accepted technical decision becomes an ARP.
- Agreed behavior becomes a specification.
- An action or implementation slice becomes an issue.
- A resolved domain term becomes part of the domain model.

## ARP threshold

Record an ARP only when the decision is:

1. costly to reverse;
2. surprising without context; and
3. the result of a meaningful trade-off.

All three should normally be true. Routine implementation choices belong in code, tests, or a pull request.

## RFC lifecycle

```text
draft -> discussion -> accepted
                    -> rejected
                    -> withdrawn
```

An accepted RFC may produce zero, one, or several ARPs. Do not duplicate the RFC discussion in the ARP; link it and record the settled decision and rationale.
