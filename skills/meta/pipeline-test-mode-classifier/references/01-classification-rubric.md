# Classification Rubric

## Decision sequence

1. Find the smallest normal upstream route.
   Prefer `test`, else a small `test_*` profile.
2. Ask whether runtime config alone is enough.
   If yes, use `profile-only`.
3. Ask whether `tests/nextflow.config` contributes required values.
   If yes, use `profile-plus-tests-config`.
4. Ask whether the current repo already assumes fixed local files.
   If yes, use `requires-local-cache`.
5. Ask whether the route is too tied to external state.
   If yes, use `unsuitable-for-generic-smoke`.

## How to recognize each case

### profile-only

Strong signals:

- `nextflow.config` includes `conf/test*.config`
- `conf/test*.config` contains concrete values for required inputs
- `tests/*.nf.test` only adds `outdir` or small scenario flags

### profile-plus-tests-config

Strong signals:

- `conf/test*.config` references `params.pipelines_testdata_base_path`
- `tests/nextflow.config` sets remote base paths or shared inputs
- `tests/*.nf.test` says "the rest is taken from shared config"

### requires-local-cache

Strong signals:

- `conf/test*.config` points to `/data/...` or another fixed local root
- comments mention locally cached files or predownloaded data
- the same pipeline once used remote URLs but the current repo test route does not

### unsuitable-for-generic-smoke

Strong signals:

- no clean runtime route is visible outside nf-test harness logic
- route depends on unavailable licenses, private datasets, or secrets
- reproducing the upstream test would need custom adapters not suitable for batch default use

## Modifiers

### localize-remote-inputs

Add when:

- `conf/test*.config` uses `http://`, `https://`, or `s3://`
- input CSV, TSV, or TXT files contain nested remote URLs
- reference bundles come from remote base paths

### environment-sensitive

Add when:

- `tests/nextflow.config` or comments mention licenses or auth
- pipeline behavior depends on cloud runner assumptions
- the normal lightweight test setup performs runtime downloads that are not optional

### igenome-sensitive

Add when:

- the selected test setup uses `genome = ...` with igenomes resolution
- server config can override igenome behavior
- reproducibility depends on explicit local reference replacement

### snapshot-rich

Add when:

- `.snap` enumerates stable output paths or small stable content blocks
- `.nftignore` shows which outputs are intentionally unstable
- assertions can be reduced to a small stable set for nextmcp smoke checks
