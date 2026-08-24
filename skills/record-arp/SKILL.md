---
name: record-arp
description: Record an accepted consequential technical decision as an ARP with its context, rationale, and consequences. Use after a decision owner has confirmed the outcome.
license: MIT
---

# Record ARP

An ARP is the project's durable technical decision record. It records an outcome; it is not a substitute for RFC discussion.

## Qualify

Normally record an ARP only when all three are true:

1. reversing the decision would be costly;
2. the choice would be surprising without context; and
3. meaningful alternatives involved a real trade-off.

If the outcome is still unresolved, use `develop-rfc`. Never invent consensus.

## Record

Read `.agents/workflows.yaml` and use the configured ARP path and prefix. Search existing records for overlap, contradiction, or supersession. Allocate the next identifier and use [the ARP template](references/arp-template.md).

Keep it concise. Link the source RFC, map ticket, meeting, or issue. Explain why the decision was selected, not the full chronology of discussion. Record non-obvious consequences.

When replacing an earlier decision, mark the old record as superseded and cross-link both records. Do not rewrite history by deleting accepted records.
