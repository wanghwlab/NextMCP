# Scope And Boundaries

This skill sits between raw upstream test configs and runtime execution through
nextmcp.

Use it when a pipeline ships a test profile that is easy to run with plain
Nextflow because the profile points at remote files, but harder to run through
nextmcp because nextmcp expects explicit server-local paths for runtime inputs.

## Config precedence boundary

- If the user asks for `conf/test.config`, treat that file as the starting point.
- Resolve referenced values such as `params.pipelines_testdata_base_path` from the normal pipeline
  runtime config chain, usually `nextflow.config`.
- Do not silently replace those values with `tests/nextflow.config`, `nf-test.config`, or
  `*.nf.test` harness overrides.
- nf-test harness files are only in scope when the user explicitly asks to reproduce the nf-test
  execution path rather than a nextmcp server-local runtime task.

## Core boundary

- The final runtime call must use server-local paths on the nextmcp server filesystem.
- A client-local path is never a valid substitute.
- Localization does not always mean copying or downloading. If a remote URL belongs to a dataset
  tree that already exists on the server, prefer mapping the URL prefix to that local root and keep
  the remaining path unchanged.
- Prefix mapping alone is not enough. After mapping, confirm that the server-local target exists.
- If a mapped target is missing, fall back to a download into the current localization root unless
  the user explicitly said that external mirror root is authoritative and must stay the only source.
- For default repository contracts, prefer a self-contained server-local bundle under the current
  localization root instead of a final contract that depends on `/data/test-datasets/...` or
  another shared mirror root.
- Treat `s3://...` URIs the same way. Prefer a known local mirror such as
  `s3://ngi-igenomes/igenomes/ -> /data/igenomes/` before attempting an S3 copy.
- nextmcp does not provide a generic HTTP download tool today.
- If the environment has no network-capable shell or fetch surface, stop and
  say the unmatched remote inputs cannot be localized yet.

## What "equivalent" means here

Equivalent does not mean byte-for-byte reproduction of every Groovy config
construct. It means preserving the same runnable test intent:

- the same input dataset
- the same reference files
- the same meaningful pipeline-facing options
- the same notable runtime expectations

For many nf-core test configs, exact equivalence can be reached with localized
files plus explicit `params`. For the remaining cases, add a small local
override config only for the runtime details that cannot be expressed as normal
pipeline params. In the current runtime, `max_cpus`, `max_memory`, and
`max_time` are one of those config-scoped cases.

## Example: `nf_pipeline/riboseq/conf/test.config`

This file shows the pattern clearly:

- direct remote files in `params`, such as `input`, `contrasts`,
  `ribo_database_manifest`, `fasta`, and `gtf`
- nested remote files inside `samplesheet.csv`, where the FASTQ columns point
  at `https://raw.githubusercontent.com/...fastq.gz`
- config-level hints in `process.resourceLimits` that describe the expected test
  scale but are not themselves pipeline params

Another common pattern appears in `nf_pipeline/sarek/conf/test.config`:

- direct `https://` test data under `modules_testdata_base_path`
- direct `s3://` reference assets such as `sentieon_dnascope_model`
- a mixed localization plan where some inputs come from a local HTTP mirror and others come from a
  local iGenomes mirror or an explicit S3 copy step

The correct outcome is not "run the config file as-is." The correct outcome is:

1. localize the remote assets into server-local paths, preferably by prefix substitution when a
   local mirror already exists, but download into the task-local bundle when that mapped target is
   absent
2. rewrite URL-bearing manifests into sibling `_local` files
3. describe the same run in plain language
4. let the runtime agent call `nextflow_run` with official params, any needed
   small override config, and server-local paths
