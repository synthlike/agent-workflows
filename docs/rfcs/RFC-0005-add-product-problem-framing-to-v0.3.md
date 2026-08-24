---
id: RFC-0005
title: Add product-problem framing to v0.3
status: accepted
authors: [synthlike]
created: 2026-08-24
decision_owner: synthlike
related_arps:
  - ../decisions/ARP-0006-add-product-problem-framing-to-v0.3.md
---

# Add product-problem framing to v0.3

## Summary

Refine the accepted [v0.3 scope](RFC-0004-focus-v0.3-on-project-feedback-workflows.md) with `frame-product-problem`: a workflow that helps a founder turn a solution-first startup idea into an explicit, challengeable problem hypothesis and customer-validation plan.

The workflow does not judge an idea from agent opinion or claim validation without customer or behavioral evidence. It interviews the founder, creates a project-owned supporting brief, generates non-leading validation questions, and later reassesses assumptions from cited evidence.

## Motivation

`establish-technical-baseline` starts from an already selected stack and deliberately avoids product-dependent architecture. The toolkit has no corresponding workflow for the product premise that should inform later domain modeling, initiatives, specifications, and architecture.

Existing workflows cover parts of the need but not the complete operation:

- `clarify-intent` resolves ambiguity in an expressed request but does not systematically challenge a startup problem hypothesis;
- `prepare-questionnaire` formats questions for another stakeholder but does not establish the assumptions the questions must test;
- `research-question` establishes focused external facts but cannot substitute for customer evidence; and
- `plan-initiative` maps multiple decisions after a destination is coherent enough to plan.

Without a dedicated boundary, an agent may reinforce the founder's proposed solution, invent an audience, ask leading questions, or describe an untested idea as validated.

## Requirements and constraints

### Requirements

- v0.3 MUST add a skill named `frame-product-problem`.
- The skill MUST interview the founder one question at a time, beginning with the highest-risk ambiguity and adapting to each answer.
- It MUST separate the proposed solution from the claimed problem, desired outcome, audience, context, trigger, current alternatives, and workaround.
- It MUST distinguish user, buyer, beneficiary, and other affected actors when those roles differ.
- It MUST classify founder belief, direct observation, external evidence, interpretation, and unknown rather than presenting them as equivalent facts.
- It MUST challenge problem frequency, consequence, underserved need, audience boundaries, counter-hypotheses, and willingness to change behavior, bear switching cost, spend time, or pay.
- It MUST remain constructive and MUST NOT treat disagreement with the founder as evidence.
- It MUST create a problem-framing brief at an existing or explicitly approved repository-contained product or discovery documentation location.
- The brief MUST be supporting evidence, not a specification, accepted decision, or validation verdict.
- It MUST identify the riskiest assumptions and define evidence that would strengthen, weaken, contradict, or leave each inconclusive.
- It MUST produce a customer-validation plan and non-leading questionnaire after founder framing is coherent.
- It MUST support later reassessment using `Unexamined`, `Supported`, `Weakened`, `Contradicted`, and `Inconclusive` evidence states.
- Reassessment MUST cite evidence and MAY recommend continue, narrow, reframe, pivot, or stop while leaving the product decision to the founder.
- It MUST route focused external facts, stakeholder questionnaires, meetings, prototypes, broad initiative planning, consequential decisions, and agreed behavior through the corresponding existing workflows and authority model.
- It MUST remain independent of industry, business model, application stack, issue backend, and agent harness.

### Constraints

- Customer and behavioral evidence cannot be fabricated or replaced by agent confidence.
- Founder answers are hypotheses or decisions, not automatically market facts.
- Interview questions must avoid pitching, confirmation bias, hypothetical compliments, and leading the respondent toward the proposed solution.
- Evidence collection must respect consent, privacy, confidential information, and project guidance.
- v0.3 remains schema 2 and retains reviewed manual updates.

### Preferences

- Prefer concrete past behavior over hypothetical future intent.
- Prefer the riskiest assumption and cheapest discriminating evidence over a broad generic survey.
- Prefer narrowing or reframing over defending the initial idea.
- Prefer links to evidence over duplicated interview transcripts.

## Non-goals

- Declaring a startup idea valid or invalid from founder discussion alone.
- Full pricing strategy, unit economics, market sizing, go-to-market design, or fundraising analysis.
- Technical feasibility or architecture selection.
- Product specification or implementation planning before the problem is sufficiently evidenced.
- Conducting customer interviews without the appropriate human participant and consent.

## Open questions

None.

## Options

### Option A: Add `frame-product-problem` to v0.3

Add one workflow spanning founder framing, a durable supporting brief, customer-validation planning, and evidence-based reassessment.

Advantages:

- completes the new-project discovery path before technical and implementation planning;
- gives the founder's assumptions an explicit challenge and evidence boundary;
- composes existing questionnaire, research, prototype, and initiative workflows; and
- prevents specifications from becoming the first place a startup premise is examined.

Disadvantages:

- expands v0.3 after its initial six-skill implementation is complete;
- requires another contract, integration, smoke test, and release digest; and
- must maintain a strict boundary against generic startup advice.

### Option B: Compose existing skills without a new workflow

Use clarification, questionnaires, research, prototypes, and initiative planning ad hoc.

Advantages:

- adds no skill or release work; and
- reuses existing operations.

Disadvantages:

- no workflow owns problem-versus-solution separation or evidence-state reassessment;
- users must know the correct composition in advance; and
- generic clarification can reinforce rather than challenge the founder's framing.

### Option C: Defer product discovery to a later release

Release the six implemented v0.3 workflows and revisit the gap later.

Advantages:

- preserves the current release candidate; and
- allows additional usage evidence.

Disadvantages:

- leaves a known high-value project-start gap; and
- separates two complementary v0.3 foundation workflows across releases.

## Recommendation

Choose Option A.

`frame-product-problem` complements `establish-technical-baseline`: one challenges the product premise, while the other establishes stack-level guardrails without inventing product architecture. Adding it before tagging v0.3 produces a more coherent new-project release despite the additional validation work.

## Resolution

Accepted by the decision owner on 2026-08-24. v0.3 expands from six to seven new workflows by adding `frame-product-problem` with founder interview, problem-framing brief, customer-validation plan, and evidence-based reassessment behavior.

The workflow may recommend continue, narrow, reframe, pivot, or stop, but it cannot claim validation without real evidence or make the founder's product decision. [ARP-0006](../decisions/ARP-0006-add-product-problem-framing-to-v0.3.md) records the roadmap refinement. The v0.3 specification is amended before implementation and release validation.
