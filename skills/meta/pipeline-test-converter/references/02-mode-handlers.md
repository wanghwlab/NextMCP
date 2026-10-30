# Mode Handlers

## profile-only

Main rule:

- build from `nextflow.config` and `conf/test*.config`

Typical output:

- chosen profile
- params from test config
- process notes from test config
- localization plan for remote URLs and `projectDir/tests/...`

## profile-plus-tests-config

Main rule:

- start from runtime config, then merge only the required shared values from `tests/nextflow.config`

Pull only the fields that matter to reproduce the setup:

- shared base paths
- shared inputs
- environment assumptions
- resource notes

Do not copy broad nf-test-only settings into the final evaluation spec without a reason.

## requires-local-cache

Main rule:

- keep the current setup explicit about the cache dependency

Output should say:

- which local root is assumed
- whether the root exists
- whether the route could later be generalized by re-localizing upstream remote inputs

## unsuitable-for-generic-smoke

Main rule:

- stop early and explain why

Useful blockers:

- license requirement
- missing secrets
- no portable data route
- route too tied to nf-test internals
