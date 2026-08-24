---
name: develop-rfc
description: Develop a technical or design RFC from unresolved ambiguity through structured discussion to an explicit outcome. Use when alternatives need analysis or multi-person agreement before implementation.
license: MIT
---

# Develop RFC

Read `.agents/workflows.yaml` and use the configured RFC path. If RFCs are not configured, ask before creating one.

## Start or resume

Search existing RFCs and ARPs for overlap. Resume the existing artifact when it asks the same material question. Otherwise allocate the next configured RFC identifier and use [the RFC template](references/rfc-template.md).

## Develop

- State the ambiguity as a decision to be made.
- Separate requirements, constraints, assumptions, preferences, and non-goals.
- Explore repository facts before asking people.
- Use `clarify-intent` for unresolved human decisions.
- Use `research-question` for external facts.
- Use `prototype-design` when higher-fidelity feedback is needed.
- Describe meaningful alternatives fairly, including doing nothing.
- Keep open questions explicit and assign a decision owner.

## Resolve

Only the decision owner can establish the outcome. Set the RFC to `accepted`, `rejected`, or `withdrawn`, and fill in its resolution.

After acceptance:

- invoke `record-arp` for each outcome meeting the ARP threshold;
- invoke `author-specification` when agreed behavior needs a coherent contract; and
- create implementation work through the configured issue backend.

Link resulting artifacts. Do not duplicate their full content in the RFC.
