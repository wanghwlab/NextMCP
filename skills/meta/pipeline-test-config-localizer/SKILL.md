---
name: pipeline-test-config-localizer
description: >-
  Use whenever the user wants to turn a pipeline `conf/test.config`,
  `conf/test_full.config`, or similar test profile into a server-local runnable
  test task for nextmcp. Trigger on requests to download remote test inputs,
  rewrite samplesheets or manifests to local paths, preserve upstream test-data
  layout, or restate raw Nextflow test config values as plain-language run
  instructions.
compatibility: >-
  Requires nextmcp runtime tools `server_info`, `fs_list`, `fs_mkdir`,
  `fs_write`, `fs_read`, `project_get`, and `nextflow_run`.
  For unmatched remote URLs, the environment also needs a network-capable shell
  or other fetch surface that can download into a server-local writable
  directory.
metadata:
  skill-class: meta
  tool-surface: nextmcp
  tool-surface-version: "2026-03-17"
  generated-from: nf-core test-profile patterns plus nextmcp runtime boundaries
  runtime-requirements: >-
    Requires nextmcp runtime tools `server_info`, `fs_list`, `fs_mkdir`,
    `fs_write`, `fs_read`, `project_get`, and `nextflow_run`.
    For unmatched remote URLs, the environment also needs a network-capable
    shell or other fetch surface that can download into a server-local writable
    directory.
---

# Pipeline Test Config Localizer

## Scope

Use this skill to convert a pipeline test config into two concrete outputs:

- a localized server-local input bundle that mirrors the upstream remote test dataset
- a natural-language execution brief that tells an agent how to run the same test through `nextflow_run`

The typical input is a file such as `<pipeline>/conf/test.config` or
`<pipeline>/conf/test_full.config`. The typical output is a directory tree
under an allowed write root, rewritten manifest files such as
`samplesheet_local.csv`, and a prose task description that hides raw parameter
names from the user-facing wording while still preserving the same run intent.

## When to use this skill

Use this skill when the user wants any of the following:

- local copies of remote test inputs referenced by a pipeline test config
- recursive download of nested remote URLs inside a downloaded CSV, TSV, or TXT manifest
- a sibling local manifest such as `samplesheet_local.csv` or `rrna-db_local.txt`
- a plain-language restatement of a test profile so the runtime agent can choose the official params itself
- a server-local test bundle that preserves the upstream directory shape closely enough for debugging

## What this skill does not handle

- replacing pipeline-specific expert skills for biological interpretation or QC review
- inventing new test inputs when the upstream config does not define them
- hiding the lack of a download surface; if no network-capable shell or fetch tool exists, stop and say so
- treating client-local paths as valid runtime paths; all final paths must live on the nextmcp server filesystem

## Authoritative assets

- `assets/workflow-rules.yaml`
- `assets/output-contract.yaml`

## References to read next

- `references/01_scope_and_boundaries.md`
- `references/02_localization_workflow.md`
- `references/03_prompt_rendering.md`

## Operating rules

- Treat the test config as a source of run intent, not as the final runtime command.
- Read the config and extract concrete assignments before you start downloading.
- When the request names a concrete source such as `conf/test.config`, resolve its referenced params
  against the pipeline runtime config chain such as `nextflow.config` first.
- Do not automatically pull base-path overrides from `tests/nextflow.config`, `nf-test.config`, or
  `*.nf.test` files into a nextmcp runtime task. Those files belong to the nf-test harness unless
  the user explicitly asks to reproduce the nf-test execution path.
- Separate three classes of facts:
  - remote input URIs that must become local files
  - local rewrite targets such as `samplesheet_local.csv`
  - descriptive run requirements that belong in prose rather than as raw config syntax
- Prefer a server-local root such as `<server_input_root>/testdata/<pipeline>/<profile_name>/`.
- Prefer prefix substitution over ad hoc download mirroring when the project or user already has a
  known server-local mirror of a remote dataset.
- Treat prefix substitution as a preferred optimization, not as proof that the target files
  already exist.
- Apply URL prefix mappings by longest matching remote prefix first. Replace only the matched URL
  prefix and keep the remaining suffix path unchanged.
- Mirror the upstream directory structure after the matched prefix as closely as practical.
- Example preferred mapping:
  - remote prefix: `https://raw.githubusercontent.com/nf-core/test-datasets/`
  - local root: `/data/test-datasets/`
  - result: `https://raw.githubusercontent.com/nf-core/test-datasets/epitopeprediction/testdata/sample.csv`
    becomes `/data/test-datasets/epitopeprediction/testdata/sample.csv`
- Example S3 mapping:
  - remote prefix: `s3://ngi-igenomes/igenomes/`
  - local root: `/data/igenomes/`
  - result: `s3://ngi-igenomes/igenomes/Homo_sapiens/GATK/GRCh38/Annotation/Sentieon/SentieonDNAscopeModel1.1.model`
    becomes `/data/igenomes/Homo_sapiens/GATK/GRCh38/Annotation/Sentieon/SentieonDNAscopeModel1.1.model`
- After a prefix map lands on a server-local path, check whether that mapped target really exists.
- If the mapped target is missing, do not stop with a pure "missing expected local mirror" result
  unless the user explicitly said that mirror root is authoritative and should not be replaced.
- When a preferred mirror path is missing and no authoritative-mirror instruction exists, fall back
  to downloading the asset into the current `localized_root` and keep the final contract
  self-contained there.
- Use `<server_input_root>/testdata/<pipeline>/<profile_name>/downloads/<host>/<remote path>` only
  as the fallback rule for unmatched URLs that really need downloading.
- For default repository contracts, prefer final runtime paths under the current `localized_root`
  rather than external shared mirror roots such as `/data/test-datasets/...`.
- Use an external shared mirror path in the final contract only when the user or project has made
  that mirror an explicit authoritative dependency for the task.
- Choose a fetch method by URI scheme when fallback download is required:
  - `https://` or `http://`: prefer `curl -L --fail -o <target> <url>`, else `wget -O <target> <url>`
  - `s3://`: prefer `aws s3 cp <url> <target>`, else `s5cmd cp <url> <target>`
- If a remote path is a directory-like prefix rather than a single file, use the recursive form of
  the same fetch tool only when the config clearly requires the whole tree.
- If no suitable fetch tool exists for the URI scheme, stop and say exactly which URI could not be
  localized and which fetch method was missing.
- When you generate or update a helper download script such as `localize_testdata.py`, make it log
  concise progress lines while it runs.
- Prefer progress logs on stderr so the script can still print one final machine-friendly result on
  stdout.
- At minimum, log whether each asset is being downloaded, reused from an existing local copy,
  rewritten into a local manifest, or finished successfully.
- A helper script may reuse an already downloaded local file, but it must still be able to fetch
  the same asset itself when that local copy is absent.
- Keep the original downloaded manifest file and write the rewritten sibling next to it with a
  `_local` suffix before the extension.
- If a manifest or reference file comes from a mapped mirror root that should stay read-only, keep
  the source file untouched and write the rewritten local copy under a writable task-local area
  such as `<server_input_root>/testdata/<pipeline>/<profile_name>/rewrites/`.
- When a downloaded structured text file contains remote URLs, recursively localize those URLs too.
- Apply the same prefix substitution rule to nested URLs inside structured text files before you
  decide whether they need downloading.
- Rewrite only true data-bearing URL fields. Ignore URLs that only appear in comments or prose.
- If a manifest cell contains multiple URLs separated by `;`, split, localize each member, and join
  them back with `;`.
- Preserve compression state. If the config points to `.fa.gz` or `.fastq.gz`, keep the local copy
  compressed unless the upstream test config explicitly expects a decompressed file.
- Prefer plain-language output for the final run brief. Do not dump raw param names into the main
  instruction unless the user explicitly asks for them.
- Keep one hidden or secondary mapping note for the runtime agent: local file path, original config
  field, and either the official parameter it should set in `nextflow_run(params=...)` or the
  server-local override config entry it should emit for `nextflow_run(config_files=...)`.
- Render a concrete `project` for the runtime brief. Prefer a stable project id such as
  `<pipeline>-test` or a user-confirmed project id, then let `nextflow_run(prepare=true)` return
  the project-owned `run_layout`.
- Treat `max_cpus`, `max_memory`, and `max_time` as config-scoped resource caps in the current
  runtime. Emit them as a small server-local override config and pass that file through
  `nextflow_run(config_files=...)`, not through `nextflow_run(params=...)`.
- `process.resourceLimits` and similar config-level runtime hints are not pipeline params. Restate
  them as an execution note or create a small local override config only when exact equivalence
  really depends on those limits.
- When the upstream route depends on concrete resource caps from the selected test config files,
  include one plain-language line in the main brief that preserves those cap values. Do not
  mention config file paths, override file names, or Groovy syntax there.
- Prefer `nextflow_run(prepare=true)` before the real launch, especially after rewriting manifests.
- Do not ask the runtime agent to set directory-layout inputs directly. Those layout paths are
  server-returned details under the chosen project.
- Use only server-local paths returned by nextmcp tools or created inside a confirmed allowed write
  root. Never send a client-local path to `nextflow_run`.
- If the upstream config mixes remote URIs and non-URI relative paths, keep the relative paths
  unchanged until you know their server-local base.

## Fast-start workflow

1. Read the config, extract assigned values, and classify remote URI params versus prose-only notes.
2. Confirm an allowed write root with `server_info()` or a user-confirmed server path.
3. Build a localization plan: first apply known URL prefix mappings, then download only the
   unmatched or missing mapped URLs into a mirrored fallback tree under the current
   `localized_root`.
4. Inspect localized manifests for nested remote URLs, apply the same mapping rule recursively, and
   emit rewritten siblings such as `samplesheet_local.csv`.
5. Write a natural-language execution brief that describes the localized test run in user terms,
   including any source-backed resource-cap summary, then let the runtime agent map that brief
   back to official params during `nextflow_run`.
