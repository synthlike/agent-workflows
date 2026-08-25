---
id: ISSUE-0044
title: "Declare backend record capabilities explicitly"
kind: "implementation"
status: open
created: 2026-08-25
assignee: 
parent: "ISSUE-0043-add-bear-for-non-issue-record-routing.md"
blocked_by:
labels: ["bear","record-routing"]
---
# Declare backend record capabilities explicitly

## Parent

Add Bear for non-issue record routing

## What to build

Make backend-supported record types and operations adapter-owned data that installed verification can enforce, allowing partial providers without letting project configuration claim unsupported behavior.

## Acceptance criteria

- [ ] Each backend type has one canonical capability declaration covering record types, common operations, and issue-extension operations.
- [ ] Local Markdown and GitHub declare their existing complete contracts without behavioral change.
- [ ] A backend may declare only the eleven non-issue types, while a future backend may declare only `issues` and its complete extension.
- [ ] Verification rejects every route whose record type or required operation is absent before any backend write.
- [ ] Project configuration has no user-authored `supports` override.
- [ ] Capability declarations, bundled assets, and tests cannot silently drift apart.

## Blocked by

None.

## Out of scope

Bear transport, Bear records, Things implementation, and dynamic reduction of required workflow semantics.

## Comments


## Resolution
