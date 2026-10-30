# Evidence Collection

## Read order

Use this order unless the user asks for a different source:

1. `<pipeline>/nextflow.config`
2. `<pipeline>/conf/test*.config`
3. `<pipeline>/tests/nextflow.config`
4. `<pipeline>/tests/*.nf.test`
5. `<pipeline>/tests/*.snap`
6. `<pipeline>/tests/.nftignore`

Do not start from repository-local support layers such as `tests/pipeline_support/`.

## What to extract

From `nextflow.config`:

- available `test` and `test_*` profiles
- which profile includes which `conf/test*.config`

From `conf/test*.config`:

- direct input and reference values
- whether values are remote, local, or relative to `projectDir`
- process-level test overrides that matter for equivalence

From `tests/nextflow.config`:

- shared test base paths
- resource limits
- auth or license assumptions

From `tests/*.nf.test`:

- whether test params are empty, minimal, or rely on shared config
- whether the route is a normal run or a stub-only route

From `.snap` and `.nftignore`:

- stable output path hints
- files intentionally excluded from stable comparison

## Evidence template

Return evidence as a short flat list. Each point should include the file and the reason.

Example:

- `nextflow.config`: `test` includes `conf/test.config`, so there is a runtime profile entry.
- `conf/test.config`: input is a remote CSV, so input localization is needed.
- `tests/nextflow.config`: shared `pipelines_testdata_base_path` is required, so runtime config alone is not enough.
- `tests/default.nf.test.snap`: stable output list exists, so compact artifact assertions are possible.
