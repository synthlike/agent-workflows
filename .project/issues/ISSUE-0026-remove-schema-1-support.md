---
id: ISSUE-0026
title: Remove schema-1 support
kind: task
status: open
created: 2026-08-24
assignee:
parent:
blocked_by: []
labels: [v0.4, cleanup, compatibility]
---

# Remove schema-1 support

## What to build

Remove the unused schema-1 compatibility surface from active code, release metadata, tests, and operational documentation. Schema 2 becomes the only readable and current consumer configuration schema.

## Acceptance criteria

- [ ] Release metadata and generated manifests list only schema 2 as readable and current.
- [ ] The source-checkout schema-1 consumer verifier and its dedicated tests are removed.
- [ ] Remaining configuration and lifecycle tests use schema 2 and retain coverage for immutable identity and unsupported-schema rejection without maintaining a schema-1 fixture.
- [ ] Operational setup, update, verification, manifest, and configuration documentation no longer advertise or route to schema-1 behavior.
- [ ] Active code, metadata, tests, and operational documentation contain no schema-1 compatibility references.
- [ ] Historical versioned RFCs, ARPs, specifications, changelog entries, and resolved issues remain unchanged as accurate decision history.
- [ ] The distribution manifest is regenerated and all repository verification passes.

## Blocked by

None.

## Out of scope

- Migrating a schema-1 consumer.
- Rewriting or deleting historical v0.1/v0.2 artifacts.
- Changing the schema-2 configuration shape.

## Comments

## Resolution
