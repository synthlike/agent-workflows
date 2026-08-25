# Bear MCP scoping and record storage

## Question

Can one Bear MCP server safely expose one project's workflow records through a root tag with nested record-kind tags?

## Verified facts

- Bear for Mac includes `bearcli`, and its MCP server exposes search, read, create, tag, and other note operations over local stdio. The documented server command is `/Applications/Bear.app/Contents/MacOS/bearcli mcp-server`. [Bear CLI documentation](https://bear.app/faq/command-line-interface/)
- `bearcli mcp-server --only-tags TAG` restricts reads, searches, and writes to notes carrying that tag or nested children. With one `--only-tags` value, `create_note` automatically injects the scope tag. Bear recommends one MCP server entry per scope. [Bear CLI documentation](https://bear.app/faq/command-line-interface/)
- Bear 2.9 lets any tag or nested subtag become a UI Workspace, filtering notes, search, archive, trash, and visible sidebar tags around that tag. The same release introduced MCP tag scoping. [Bear 2.9 Workspace announcement](https://blog.bear.app/2026/07/bear-2-9-use-tag-as-workspace/)
- Nested tags use slash separators. CLI list filtering by a parent tag includes notes carrying nested child tags. Bear supports note IDs, title-based lookup, tags, Markdown tasks, and wikilinks. [Bear CLI documentation](https://bear.app/faq/command-line-interface/)
- MCP whole-note overwrite requires a `baseHash`, so stale whole-note writes can be rejected. The CLI and MCP intentionally differ where structured write gating is useful. Local help from the installed `bearcli mcp-server` and `bearcli help all`, inspected 2026-08-25.
- Bear states that the CLI and MCP server read and write the local Bear database, send no telemetry, cannot access encrypted note content, and should be used after making a backup. [Bear CLI documentation](https://bear.app/faq/command-line-interface/)

## Interpretation

A stable root such as `agent-workflows/<project-key>` can be both the project's Bear Workspace and the MCP server's single included tag. Nested child tags such as `research`, `meetings`, and `specs` can classify semantic record types without coupling notes to workflow skill names. Configuration should use note IDs for mutation, retain stale-write tokens, and keep mutable lifecycle state in structured content rather than tags.

## Remaining uncertainty

The exact Things MCP operation set and its ability to implement the complete issue contract require separate primary-source research. Bear issue semantics such as comments, claims, dependencies, cancellation, and frontier traversal would be emulated in structured notes and need contract tests before support can be claimed.
