# Semantic record adapter contract

A record adapter persists one configured semantic record type without exposing provider mechanics to workflows.

## Portable request

Every request carries:

- `operation`: `create`, `read`, `list`, `update`, or `archive`;
- named backend instance;
- semantic record type;
- complete typed destination; and
- operation-specific identity, title, content, query, semantic identifier, or expected revision.

Create allocates identity inside the write. Update and archive require the opaque revision returned by read. Workflows do not construct provider IDs, paths, URLs, or revisions.

## Portable response

A stored record returns:

- semantic record type;
- semantic ID;
- title and canonical content;
- provider metadata;
- opaque revision; and
- a structured reference containing backend instance, native stable ID, title, and optional href.

The destination adapter renders structured references for its own canonical content. Workflows pass the complete reference unchanged and never construct provider links.

List and search return zero or more complete stored records in stable adapter order.

## Stable errors

Adapters raise a machine-readable code and safe message. The initial portable codes include:

- `invalid_request`;
- `invalid_destination`;
- `invalid_id`;
- `unsupported_operation`;
- `unsupported_record_type`;
- `backend_mismatch`;
- `not_found`;
- `duplicate_id`;
- `stale_revision`;
- `malformed_record`;
- `malformed_reference`;
- `archived_record`;
- `claim_conflict`;
- `invalid_state`;
- `invalid_relationship`;
- `broken_reference`; and
- `io_error`.

A failed operation must not partially mutate a record. A stale revision must fail without writing.

## Issue extension

An adapter receiving the `issues` route additionally implements:

- create, read, list, and guarded update;
- chronological comment;
- conflict-aware claim;
- distinguishable resolve and cancel;
- add or remove parent relationships;
- add or remove blockers; and
- deterministic frontier traversal.

Every issue mutation requires the latest opaque revision. A frontier issue is open, unassigned, a direct child of the parent, and blocked only by resolved issues. Cancelled blockers do not satisfy dependencies.

## Local reference scope

The local reference adapter supports all twelve record routes. Eleven non-issue types use embedded machine-readable metadata, exact-byte revisions, consumer-root-relative structured references, and retained archive state. ARPs and RFCs allocate prefixed identifiers; other records allocate collision-safe slugs.

Issues retain the established Markdown frontmatter, lifecycle states, comment and resolution sections, relative relationships, and stable filename ordering. Claims and allocation remain non-atomic across unsynchronized working trees.

## GitHub reference scope

The GitHub adapter supports all twelve routes with exactly one `workflow:record:*` label per managed object and one additional `workflow:issue:*` label for issue-routed objects. Non-issue records close as completed after publication, retain semantic lifecycle in canonical metadata and content, and remain revision-updatable. Searches include open and closed issues, exclude pull requests, and detect duplicate semantic IDs. Issue routes retain explicit identity verification, native relationships, close reasons, complete pagination, and claim-conflict behavior.

Every later adapter must run the shared record conformance suite and, when issue-capable, the issue extension suite rather than redefining these semantic shapes.
