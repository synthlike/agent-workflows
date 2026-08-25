# Issue-tracker backend contract

Every backend must define the following semantic operations:

1. **Create:** create an issue with a title, body, kind, and optional labels.
2. **Read:** retrieve the complete issue, metadata, and discussion.
3. **List:** filter issues by state, kind, label, parent, and assignee where supported.
4. **Update:** change title, body, state, labels, or other metadata.
5. **Comment:** append chronological discussion without rewriting the original question.
6. **Claim:** mark an issue as owned before substantive work begins.
7. **Resolve:** record the answer or outcome and close the issue.
8. **Cancel:** close work that is no longer in scope without treating it as a decision.
9. **Parent:** link a child issue to its map or source issue.
10. **Block:** add or remove dependencies between issues.
11. **Frontier:** find open, unblocked, unclaimed children in stable order.

## Required semantics

- An issue has one stable identity.
- A claim is the first write in a work session.
- Resolutions and cancellations are distinguishable.
- A blocker is satisfied only when resolved, not merely claimed or cancelled, unless project policy explicitly says otherwise.
- Human-readable references use linked titles, not bare identifiers.
- The map is an index. Detailed answers live in the resolved child issue.
