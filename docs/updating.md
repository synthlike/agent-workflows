# Updating

Skills are intended to be vendored and versioned with the consumer repository.

An update should:

1. compare the installed source version with the new release;
2. display relevant changelog entries;
3. detect locally modified skill files;
4. update reusable files only;
5. preserve project configuration and all project artifacts; and
6. run structural verification.

Until an updater is provided, update through the same Agent Skills installer used for installation and review the resulting diff before committing.
