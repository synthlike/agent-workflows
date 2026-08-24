# Updating

Skills are vendored and versioned with the consumer repository. The installed lifecycle automates fresh-project dependency completion and verification, but does not provide reusable update planning, replacement, rollback, interruption recovery, configuration migration, or artifact migration.

## Ownership boundary

An update may replace only unmodified, distribution-managed skill directories. The consumer owns and an installer must preserve:

- `.agents/workflows.yaml`;
- root agent guidance and `docs/agents/`;
- issue-backend state;
- all project artifacts; and
- explicit local modifications to vendored skills.

Changing recorded distribution identity after accepting an update is an explicit consumer configuration change, not an installer overwrite.

## Reviewed update procedure

1. From the currently installed `configure-project`, [verify the installation](verifying-installation.md) against its embedded manifest. Stop if verification surfaces locally added, missing, or modified skill files; the lifecycle will not merge them automatically.
2. Compare `.agents/workflows.yaml`'s exact `distribution.source` and `distribution.version` with the proposed release and review the intervening changelog entries.
3. Use an Agent Skills-compatible installer or an equivalent manual copy to replace only the intact, dependency-closed vendored skill selection. Third-party installer update behavior is not guaranteed.
4. Review the complete diff. Consumer-owned configuration, guidance, backend state, and artifacts must remain unchanged.
5. Resolve any local skill changes explicitly instead of allowing silent overwrite.
6. Recalculate selected-workflow closure against the target release and review any dependency additions or removals.
7. After accepting the installed source, update `distribution.source`, `distribution.version`, and schema-2 skill inventory through a reviewed consumer change.
8. Run installed verification from the new `configure-project` and commit the reviewed update.

Do not proceed when an installer cannot surface conflicts or preserve consumer-owned files. `configure-project` verifies installations but never installs or replaces skill directories. Migration, when required, remains separate explicit work. General update transactions and recovery remain future work and may be reprioritized when adoption or demonstrated update pain warrants it.
