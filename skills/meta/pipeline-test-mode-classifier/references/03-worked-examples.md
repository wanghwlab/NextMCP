# Worked Examples

These examples are from the vendored pipelines in this repository.

## epitopeprediction

- Primary mode: `profile-plus-tests-config`
- Modifiers: `localize-remote-inputs`, `snapshot-rich`
- Why:
  - `conf/test.config` uses `params.pipelines_testdata_base_path`
  - `tests/nextflow.config` defines that base path
  - `default.nf.test.snap` provides a large stable artifact list

## fetchngs

- Primary mode: `profile-only`
- Modifiers: `localize-remote-inputs`, `environment-sensitive`
- Why:
  - `conf/test.config` already gives a concrete remote input CSV
  - `tests/main.nf.test` contains explicit output assertions
  - runtime behavior still depends on downloading public sequence data

## riboseq

- Primary mode: `profile-only`
- Modifiers: `localize-remote-inputs`, `snapshot-rich`
- Why:
  - `conf/test.config` provides concrete remote inputs and references
  - `main.nf.test.snap` is rich enough to derive compact stable assertions

## rnaseq

- Primary mode: `requires-local-cache`
- Modifiers: `snapshot-rich`
- Why:
  - current `conf/test.config` points to `/data/rnaseq_test_data/...`
  - route assumes a prelocalized local bundle, not a generic remote-first test

## sarek

- Primary mode: `profile-only`
- Modifiers: `localize-remote-inputs`, `igenome-sensitive`, `snapshot-rich`
- Why:
  - `test` includes `conf/test.config`
  - config mixes local `projectDir/tests/...` files and remote references
  - route depends on `genome = testdata.nf-core.sarek`
  - server-side `igenomes_ignore` can change that behavior

## scrnaseq

- Primary mode: `profile-plus-tests-config`
- Modifiers: `localize-remote-inputs`, `snapshot-rich`
- Why:
  - `conf/test.config` defines the basic route
  - `tests/nextflow.config` duplicates shared test values and resource constraints used by test files
  - snapshot material exists for stable outputs
