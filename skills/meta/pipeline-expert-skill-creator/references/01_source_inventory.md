# Source Inventory

## Authoring collection paths

Use one of these two equivalent authoring inputs, then keep the rest of the workflow the same.

### Path A: nextmcp inspect payload

1. use `nextflow_list_pipelines` only if the server-visible pipeline ID is not already known
2. use `nextflow_inspect_pipeline(detail="materials")` to fetch the standard source payload
3. use `fs_read` only for targeted extra files that are outside that payload
4. read MCP tool docstrings and input schemas for the shared nextmcp tools
5. read legacy skills or prompts only for migration clues

### Path B: repository-local inspect-equivalent bundle

1. resolve the pipeline directory, for example `nf_pipeline/rnaseq` or `nf_pipeline/riboseq`
2. build the same top-level authoring payload shape used by
   `nextflow_inspect_pipeline(detail="materials")`
3. read targeted extra files only when they are outside that standard bundle
4. read MCP tool docstrings and input schemas for the shared nextmcp tools
5. read legacy skills or prompts only for migration clues

Use `scripts/build_authoring_bundle.py` as the default v1 path for repository-local collection so
the bundle shape stays aligned with `src/nextmcp/nextflow_catalog.py`.

For the repository-local bundle, mirror `src/nextmcp/nextflow_catalog.py` instead of inventing a
broader file dump:

- `schema`: parsed `nextflow_schema.json`
- `documents`: `README.md` as `{"role": "readme", ...}` plus top-level `docs/*.md` files as
  `{"role": "doc", ...}`
- `source_files`: `main.nf` as `main_script`, optional `nextflow.config` as `nextflow_config`,
  top-level alternate `*.nf` files other than `main.nf` as `entry_script`, and top-level
  `workflows/*.nf` files as `workflow_script`

Keep the same descriptor keys the tool returns: `role`, `path`, and `content`. Prefer resolved
repository paths so the bundle stays close to the server payload shape.

`nextflow_inspect_pipeline(detail="materials")` is still the default authoring path when a live
server is available. The repository-local bundle is the fallback for source-checkout workflows, not
an excuse to widen the standard payload.

## Priority order inside collected materials

Treat facts in this order once the files are in hand:

1. pipeline source and config files
2. `nextflow_schema.json`
3. official pipeline docs
4. MCP tool metadata
5. legacy skills and prompts

Targeted `fs_read` extras should be classified back into one of the first three buckets instead of
becoming an independent source tier.

Before rendering anything, do one capability sweep across those materials. Look for booleans,
enums, extra entry scripts, output sections, and tests that signal significant optional modes.
Typical examples are `with_umi`, `use_sentieon_star`, `skip_alignment` plus
`skip_pseudo_alignment`, `kraken2_bracken`, `STEP_BUILD_STAR_INDEX`, and
`STEP_ASSEMBLE_STRINGTIE`.

## Standard inspect payload map

### `schema`

This is the parsed `nextflow_schema.json` payload.

Capture:

- current parameter names
- required inputs
- enum values and defaults
- preset candidates and placeholder values
- high-impact switches that imply a real route, runtime prerequisite, or output family
- grouping cues for progressive disclosure, such as path-like inputs, references, route booleans,
  enums, output controls, and lower-impact tuning fields that still need exact lookup coverage

### `documents`

This is the README plus top-level `docs/*.md` content returned by the tool.

Typical examples:

- `README.md`
- `docs/usage.md`
- `docs/output.md`

Capture:

- user-facing scenarios
- output review order
- QC interpretation and troubleshooting
- optional modes that materially change how outputs should be interpreted

### `source_files`

This is the inlined Nextflow source payload returned by the tool.

Typical roles:

- `main_script`
- `nextflow_config`
- `workflow_script`
- `entry_script`

Typical examples:

- `main.nf`
- `nextflow.config`
- `interactive.nf`
- `test_fastq_align_star.nf`

Capture:

- pipeline identity, modes, and execution boundaries
- emitted artifacts and output directories
- assumptions hidden in configs, entry scripts, or channel wiring
- alternate entry workflows and build-only or assembly-only steps that need explicit recipes

### `fs_read` extras

Use targeted `fs_read` only when a file that materially changes the expert skill is not already in
the standard inspect payload.

Examples from `nf_pipeline/rnaseq`:

- `workflows/rnaseq/main.nf` for nested workflow logic
- `docs/usage/differential_expression_analysis/*.md` for deeper user guidance
- extra config or asset files that are referenced by the top-level docs
- selected tests such as `tests/umi.nf.test` when a high-impact optional mode needs confirmation

If the server exposes relevant tool docstrings and input schemas, treat them as part of the local
MCP integration material. They define how the generated expert skill should call shared tools at
runtime. Keep that runtime contract separate from the collection path above: the generated package
should teach optional `server_info()`, optional `project_list()`, optional
`project_get(project)`, and `fs_list(mode="manifest")` only when uncertainty
still exists, optional `nextflow_run(prepare=true)` for launch planning,
`nextflow_run` to launch, `run_list` for historical-run recovery when artifact
reuse matters, `run_get(include=[...])` before raw logs, `run_artifacts(...)`
for artifact sections, `run_logs` when summarized state is not enough,
`fs_read` for explicit runtime files, and only use `nextflow_list_pipelines`
when it needs a server-local pipeline root for an alternate entry script. It
should also state explicitly that runtime `path` values, the `project`
identifier, and relative path-like values in `params` or `config_files` are
server-side, not client-local. If the pipeline has reusable historical
outputs, the generated package should teach `artifact_path_contains`,
`artifacts.json`, `pipeline_fingerprint`, and route-confirming files such as
`pipeline_info/params.json` as part of the reuse workflow.

Legacy skills are migration clues only. If legacy prose conflicts with current schema or code,
rewrite it from the current structured sources instead of copying it forward.

## Full schema retention with progressive disclosure

The generated expert skill should keep full current `nextflow_schema.json` coverage, but not as one
flat dump.

Instead, preserve it in a progressive disclosure structure:

- one compact route-shaping parameter guide for ordinary planning
- one schema index that lists every grouped parameter reference file
- grouped schema-backed parameter files that preserve the full parameter set for exact lookup

The grouped files should let a runtime agent answer questions such as:

- which exact field name controls this mode
- whether the field is required
- what type or enum values the field allows
- what default the current schema declares
- whether the field belongs in the compact route guide or only in the full lookup layer

Grouping should follow the original top-level `nextflow_schema.json` section layout when that
layout is available through root `allOf` plus the referenced `definitions` or `$defs` entries.
This preserves the pipeline author's own organization and avoids inventing cross-pipeline buckets
too early.

When a schema does not expose a stable top-level section layout, fall back to stable parameter
behavior rather than arbitrary alphabet slices. In that fallback mode, use heuristic groups such as
path-like inputs, references, route selectors and booleans, enum or choice parameters, output or
reporting controls, and lower-impact tuning or metadata fields. Full coverage must remain complete
and discoverable through the schema index in either mode.
