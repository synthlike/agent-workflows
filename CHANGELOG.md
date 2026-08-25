# Changelog

## Unreleased

- Replace schema 2 with explicit schema-3 routing for all twelve semantic record types across local Markdown and GitHub backends.
- Validate routes against immutable adapter-owned capability declarations so future note-only and issue-only backends cannot claim unsupported behavior.
- Add scoped Bear configuration, read-only MCP provider preflight, and complete non-issue record operations while keeping `issues` on another backend.
- Distinguish integrity-checked discovery from model invocation eligibility and defer GitHub or Bear inspection until each backend is considered.
- Rename the mandatory workflow bootstrap from `configure-project` to `configure-workflows` before external adoption.
- Complete the GitHub Cloud issue backend with explicit multi-account identity selection, native relationships, reviewed label provisioning, deterministic frontier calculation, and an executable `gh` helper.
- Configure repository retention and paths for research, questionnaires, technical baselines, prototypes, and handoffs according to project needs.
- Restructure the README around user outcomes, scenario-based workflow selection, a short setup path, and a copyable founder-discovery prompt.
- Require complete skill installation and remove the custom archive distribution and missing-skill application mechanism.

## 0.4.0 - 2026-08-24

- Remove the unused schema-1 compatibility verifier and retain schema 2 as the sole supported configuration.
- Make operational documentation, smoke testing, and release verification less version-specific.
- Consolidate repeated consumer fixtures and skill-contract assertions.
- Ignore generated release assets and Python or test caches.

## 0.3.0 - 2026-08-24

- Add `frame-product-problem` for founder interviews, problem briefs, customer-validation planning, and evidence reassessment.
- Add `establish-technical-baseline` for minimal production-compatible foundations from an agreed stack.
- Add issue triage, diagnosis-only failure investigation, and durable regression capture workflows.
- Add read-only implementation conformance review and evidence-based initiative closure.
- Retain schema 2 and reviewed manual updates; provisionally defer transactional maintenance automation to v0.4.

## 0.2.0 - 2026-08-24

- Add deterministic v0.2 release manifests and self-contained validated bundles.
- Add schema-2 installation inventory and source-checkout-free installed verification.
- Add dependency-complete fresh-project planning and non-destructive missing-skill installation.
- Give generated workflow guidance a project-overridable plain-language documentation style.
- Validate the fresh flow through `skills@latest` and Pi while preserving existing-project conventions and lazy artifact directories.
- Defer reusable update transactions, rollback, recovery, and public migration tooling to v0.3.

## 0.1.0 - 2026-08-24

- Establish the independent workflow-kit structure and consistent verb-object skill vocabulary.
- Add configurable GitHub and local-Markdown issue backends.
- Add workflows for domain modeling, RFCs, ARPs, meetings, initiative planning, specifications, and implementation planning.
- Define the behavior-based vendored installation and consumer-project ownership contract.
- Require immutable distribution identity and dependency-closed selective installations.
- Add source, dependency, consumer-installation, and documentation-link verification.
- Document new-project setup, existing-project adoption, customization, and reviewed non-migrating updates.
