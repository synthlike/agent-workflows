# Customizing

Project policy overrides toolkit defaults. Prefer changing `.agents/workflows.yaml` and project documentation over editing installed skills.

Edit a skill only when the workflow itself differs. Record local modifications before updating vendored skills so they are not overwritten silently.

New issue backends must implement every operation in `backends/issue-tracker/contract.md`. New skills should use lowercase verb-object names and keep implementation details in references where possible.
