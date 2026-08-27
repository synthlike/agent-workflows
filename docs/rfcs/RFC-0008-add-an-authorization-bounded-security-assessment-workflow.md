<!-- agent-workflows-record
{"archived":false,"created":"2026-08-27T18:31:48Z","id":"RFC-0008","modified":"2026-08-27T18:31:48Z","record_type":"rfcs","title":"Add an authorization-bounded security assessment workflow"}
-->
---
id: RFC-0008
title: Add an authorization-bounded security assessment workflow
status: draft
authors: [synthlike]
created: 2026-08-27
decision_owner: synthlike
related_arps: []
---

# Add an authorization-bounded security assessment workflow

## Summary

Consider a manually invoked `assess-security` skill for bounded, authorized security testing of code and systems. Start with one orchestration skill that reuses existing investigation, regression, and implementation-review workflows. Add specialized security skills only when concrete gaps justify them.

## Motivation

Developers need help finding security weaknesses before release, including authorization errors, injection, unsafe configuration, dependency exposure, secret leakage, tenant isolation failures, and abuse cases. Generic code review does not establish authorization boundaries, active-test approvals, rate limits, evidence handling, or security-specific stop conditions.

Security testing is dual-use. The workflow must support legitimate testing without turning an ambiguous request into uncontrolled scanning, destructive exploitation, persistence, evasion, credential theft, social engineering, or testing of third-party systems.

## Requirements and constraints

### Authorization and scope

- Require manual invocation; the skill should declare `disable-model-invocation: true` where the harness supports it.
- Establish the authorized owner, target, environment, time window, and excluded systems before active testing.
- Treat repositories, hosts, accounts, tenants, credentials, and third-party dependencies outside the confirmed scope as unauthorized.
- Stop when target ownership or authorization is unclear.
- Keep production testing opt-in and separately approved.

### Progressive testing

- Begin with repository inspection, architecture facts, existing controls, and a lightweight threat model.
- Produce a concrete test plan that identifies tools, targets, expected traffic, test data, rate limits, possible side effects, and stop conditions.
- Separate passive/local checks from network activity and potentially destructive tests.
- Request explicit approval before network activity, provider mutations, elevated access, high-volume testing, or tests that may affect availability or data.
- Prefer local fixtures, disposable environments, synthetic identities, and non-destructive proofs.
- Do not perform persistence, stealth/evasion, social engineering, uncontrolled exfiltration, denial of service, or destructive payload execution.

### Evidence and findings

- Record only the minimum evidence needed to reproduce and assess a finding.
- Redact credentials, tokens, personal data, unrelated customer data, and exploit material that is not needed for remediation.
- Distinguish hypotheses, suspected findings, reproducible vulnerabilities, accepted defects, and verified remediations.
- Do not claim security, safety, or absence of vulnerabilities from incomplete testing.
- Triage confirmed actionable findings through the configured issue route.
- Use `investigate-failure` to establish root cause when behavior remains uncertain.
- Use `capture-regression` after a reproducible vulnerability is accepted as a defect.
- Use `review-implementation` to compare a remediation with authoritative intent.
- Keep assessment notes as supporting evidence rather than authoritative requirements or decisions.

### Tool independence

- Keep `assess-security` semantic and independent of language, framework, scanner, CI system, or agent harness.
- Put concrete integrations such as Semgrep, CodeQL, OSV-Scanner, dependency auditors, secret scanners, fuzzers, ZAP, Burp, or Nuclei in optional backend/reference documents.
- Never infer authorization merely because a tool is installed or a target is reachable.

## Non-goals

- General-purpose offensive operations against arbitrary targets.
- Testing systems without explicit authorization.
- Automated exploitation, persistence, evasion, social engineering, credential harvesting, or denial of service.
- Replacing professional penetration testing, legal review, incident response, or a secure development program.
- Guaranteeing that a system is secure because the planned checks passed.
- Creating a new security-report record type before a demonstrated need exists.

## Proposed workflow

1. Confirm manual invocation and authorization.
2. Define targets, exclusions, environment, test identities, time window, and stop conditions.
3. Inspect repository evidence and existing security controls without active external interaction.
4. Build a threat-informed test inventory and classify each check by risk.
5. Present the exact active-test plan and request approvals by risk boundary.
6. Execute only approved checks, stopping on unexpected impact or scope ambiguity.
7. Preserve concise, redacted evidence and label confidence and reproducibility honestly.
8. Route uncertain behavior to `investigate-failure`.
9. Propose confirmed findings for issue triage before any issue write.
10. Encode accepted reproducible defects through `capture-regression` without adding further exploit behavior.
11. After remediation, rerun the smallest approved checks and use `review-implementation` for conformance.
12. Report tested scope, untested scope, limitations, findings, and residual uncertainty.

## Candidate skill boundaries

### `assess-security`

New orchestration skill. Defines authorization and scope, develops a threat-informed plan, gates active testing, gathers bounded evidence, and proposes next workflows.

### `investigate-failure`

Existing skill. Reuse it for suspected vulnerabilities when root cause or reproducibility is uncertain. A separate `investigate-vulnerability` skill would initially duplicate this behavior.

### `capture-regression`

Existing skill. Reuse it to encode an accepted security defect as the smallest durable automated check without implementing a fix.

### `review-implementation`

Existing skill. Reuse it to assess whether a remediation conforms to the accepted issue, specification, or decision.

### Possible future `verify-remediation`

Add only if remediation verification needs a distinct contract for re-running active security checks, comparing evidence, and recording residual exposure. Initially this can remain a phase of `assess-security` plus `review-implementation`.

### Possible future `model-threats`

Add only if projects need threat modeling independently of an assessment. Initially keep a lightweight threat model inside `assess-security`.

## Open questions

- What minimum evidence establishes that the requester is authorized to test a target?
- Should scope and approval be represented only in the conversation, in an assessment journal, or in another supporting artifact?
- Which risk classes require separate approvals, and which local read-only checks may run under the initial invocation?
- Should all network access require approval, including requests to localhost and disposable test environments?
- How should the workflow detect and handle production endpoints embedded in configuration?
- What evidence may be persisted when findings contain sensitive exploit details or secrets?
- Should security findings use ordinary issues with labels, or is a restricted disclosure mechanism eventually needed?
- Which concrete tool references should ship first while keeping the semantic skill stack-independent?
- What exact completion state distinguishes “planned checks passed” from “remediation verified” without implying broad security assurance?

## Options

### Option A: Add only `assess-security` and reuse existing workflows

Introduce one manually invoked orchestration skill. Delegate uncertainty, regression capture, and remediation review to existing skills. This minimizes overlap and lets usage reveal missing boundaries.

### Option B: Add a complete security skill family immediately

Introduce `model-threats`, `assess-security`, `investigate-vulnerability`, and `verify-remediation` together. This gives every phase a name but risks duplicated behavior and premature contracts.

### Option C: Add tool-specific scanning skills

Create separate skills around individual scanners or ecosystems. This is quick for one stack but conflicts with the repository requirement that workflows remain application-, language-, and harness-independent.

### Option D: Do not add a security workflow

Continue using generic investigation and review skills. This avoids dual-use complexity but leaves authorization, active-test approvals, rate limits, evidence handling, and stop conditions implicit.

## Recommendation

Start with Option A. Design `assess-security` as a manually invoked, authorization-bounded orchestration skill and reuse `investigate-failure`, `capture-regression`, and `review-implementation`. Treat `model-threats`, `investigate-vulnerability`, and `verify-remediation` as candidate future skills, not committed scope. Keep concrete scanners in references and require separate approval for active network or potentially harmful operations.

## Resolution

Unresolved draft. No skill, specification, ARP, or implementation issue has been created.
