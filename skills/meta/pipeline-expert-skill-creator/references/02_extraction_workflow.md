# Extraction Workflow

## Fixed order

Follow this sequence without skipping ahead to prose:

0. use the general-purpose `skill-creator` skill to drive the skill-authoring and evaluation loop
1. resolve the pipeline ID or repository-local pipeline path
2. collect the standard `nextflow_inspect_pipeline(detail="materials")` payload or build the same
   inspect-equivalent payload from the repository pipeline tree
3. collect only the targeted extra files still missing from that payload
4. generate grouped schema assets
5. run `scripts/audit_capabilities.py` and keep `assets/capability-audit.yaml`
6. build a structured pipeline model
7. scaffold the package and fill assets
8. resolve `assets/authoring-gaps.yaml`
9. render references from those assets
10. render `SKILL.md`
11. run `scripts/validate_expert_skill.py`, then finish manual validation
12. create offline eval prompts from `evals/templates/expert-skill-evals.json` and run them through
    `skill-creator` or `scripts/run_offline_evals.py`

## Structured pipeline model

`skill-creator` is the professional skill-creation package. In this workflow, it owns the generic
draft, eval, and iteration loop. This skill provides the pipeline-specific source gathering and
rendering rules that the loop should follow.

Use the tool surface in this order when the pipeline is available through nextmcp:

1. `nextflow_list_pipelines`
2. `nextflow_inspect_pipeline(detail="materials")`
3. `fs_read` only for extra files outside the standard inspect payload
4. MCP tool descriptions and input schemas for `project_*`, `run_*`, `fs_*`, and `nextflow_*`

When the user points at a repository-local pipeline checkout instead of a running nextmcp server,
build the same authoring payload shape before extracting facts:

- `schema` comes from `nextflow_schema.json`
- `documents` include `README.md` plus top-level `docs/*.md` with the same `readme` / `doc` roles
- `source_files` include `main.nf`, optional `nextflow.config`, top-level alternate `*.nf`
  entries, and top-level `workflows/*.nf` files with the same `main_script`,
  `nextflow_config`, `entry_script`, and `workflow_script` roles
- nested workflow files such as `workflows/rnaseq/main.nf` remain targeted extras, just as they do
  outside the standard inspect payload

Do not skip the normalization step. The rest of the extraction flow should consume one stable
bundle shape whether the starting point was `nextflow_inspect_pipeline(detail="materials")` or a
repository path such as `nf_pipeline/rnaseq`.

Do not copy this collection order into the generated expert skill as its runtime playbook. The
generated skill should already contain the pipeline contract and should not tell the runtime agent
to re-run `nextflow_inspect_pipeline` for ordinary planning.

Break the inspect payload apart before extracting facts:

- `source_files` answer workflow shape, execution modes, and artifact flow
- `schema` answers parameter names, defaults, required inputs, and preset seeds
- `documents` answer user scenarios, output review order, QC meaning, and troubleshooting

When the pipeline documents reusable outputs or source files publish durable handoff artifacts,
capture the reuse facts explicitly instead of leaving them implied:

- which named files or subpaths a runtime agent is likely to remember
- whether those files should map to `artifact_path_contains` examples
- which metadata files confirm route compatibility, such as `pipeline_info/params.json`
- whether `artifacts.json` and `pipeline_fingerprint` should be treated as required reuse facts

For `nf_pipeline/rnaseq`, expect the first useful pass to come from `nextflow_schema.json`,
`README.md`, `docs/README.md`, `docs/usage.md`, and `docs/output.md`. Then use targeted `fs_read`
or direct repository reads if you still need deeper files such as `workflows/rnaseq/main.nf` or
`docs/usage/differential_expression_analysis/rnaseq.md`.

Do a deliberate capability audit before you start writing assets. Ask:

- which booleans or enums create a real route instead of a minor tweak
- which modes add runtime prerequisites outside normal params
- which alternate entry scripts or step-local workflows need explicit recipes
- which outputs would materially affect user interpretation or reuse

If the answer is "we are not covering this capability", write down the reason now so the generated
expert skill can explicitly scope it out instead of silently omitting it.

Use `scripts/audit_capabilities.py` as the first pass for this audit. The script is intentionally
conservative: it marks likely high-impact schema params, alternate entries, step names, documented
outputs, and runtime prerequisites as `needs_review`. The agent must then cover each item in the
listed assets or mark it `scoped_out` with a source-backed reason.

Before editing `SKILL.md`, write down at least these facts:

- pipeline identity and supported modes
- required inputs and placeholders
- scenario playbooks
- reusable artifacts
- QC rules
- troubleshooting routes
- significant optional capabilities or explicit scope-outs
- a complete grouped parameter inventory derived from the current schema

If one of these areas is still empty, the package is not ready for prose rendering.

## Asset mapping

Map extracted facts into assets before writing references:

- `pipeline-profile.yaml`: pipeline identity, modes, assumptions, limitations
- `playbooks.yaml`: user-intent routes and outputs to review
- `step-recipes.yaml`: tool call order, minimal inputs, process checkpoints
- `param-presets.yaml`: schema-backed presets and placeholders
- `schema-index.yaml`: lightweight grouped index into the full current parameter inventory
- `schema-groups/*.yaml`: complete grouped parameter definitions for progressive disclosure
- `capability-audit.yaml`: explicit list of high-impact modes, outputs, prerequisites, and entry
  points that must be covered or scoped out
- `authoring-gaps.yaml`: scaffold todo list that must be resolved before the package is runtime-ready
- `artifact-contracts.yaml`: published files, output directories, downstream handoff meaning
- `qc-rules.yaml`: QC good/bad signals, likely causes, and next actions

For the grouped schema layer, prefer the reusable generator path over hand-grouping:

- start from `scripts/generate_schema_groups.py`
- feed it the current `nextflow_schema.json`
- add a small override file only when one pipeline needs corrected grouping, placeholder, channel,
  or mapping-note decisions
- review the generated `schema-index.yaml` and `schema-groups/*.yaml` before editing references

For repository-local collection, prefer the reusable bundle builder over ad hoc file reads:

- start from `scripts/build_authoring_bundle.py`
- treat its JSON output as the repository-local equivalent of
  `nextflow_inspect_pipeline(detail="materials")`
- add targeted extra reads only when one needed file falls outside that standard bundle

For the first package draft, prefer the reusable scaffold step over hand-creating every file:

- start from `scripts/scaffold_expert_skill.py`
- point it at one authoring bundle JSON plus the target expert skill directory
- treat the result as a starter package that still needs source-backed refinement
- do not treat the starter package as runtime-ready while `assets/authoring-gaps.yaml` contains
  open gaps or `assets/capability-audit.yaml` contains `needs_review` items

For the first eval set, create one mixed-source `evals/evals.json`:

- start from `evals/templates/expert-skill-evals.json` or the scaffold generator output
- include `source` on every eval item: `asset`, `authoring_bundle`, or `audit`
- use `source_materials` to show which assets or authoring bundle facts justify the eval
- fill asset-derived prompts from `pipeline-profile.yaml`, `playbooks.yaml`,
  `param-presets.yaml`, `artifact-contracts.yaml`, and `qc-rules.yaml`
- fill source-derived coverage prompts from the normalized authoring bundle, capability audit,
  and authoring gaps so the eval set can catch important facts missing from the skill
- keep these evals offline by default; they test route selection, parameter-channel mapping,
  output/QC review order, historical reuse planning, and source-backed coverage
- use `scripts/run_offline_evals.py --skill-root <skill-dir>` for a local one-command run that
  saves each prompt, response, timing file, grading file, and iteration summary; pass
  `--agent kimi` to run the same prompts through Kimi CLI
- do not launch Nextflow from these evals unless the user explicitly asks for a real integration
  run; use the pipeline smoke-test contract workflow for actual run completion checks

For significant optional capabilities, do not stop at one asset if the mode clearly needs more:

- if a capability changes user intent, add a playbook
- if it changes the launch shape, add a preset
- if it changes entry selection or sequencing, add a step recipe
- if it creates special outputs, add an artifact contract
- if it changes interpretation or common failures, add QC or troubleshooting coverage

Route facts by source type:

- `source_files` mainly feed `pipeline-profile.yaml`, `step-recipes.yaml`, and
  `artifact-contracts.yaml`
- `schema` mainly feeds `param-presets.yaml`, `schema-index.yaml`, `schema-groups/*.yaml`, and
  parameter boundary notes
- `documents` mainly feed `playbooks.yaml`, `artifact-contracts.yaml`, and `qc-rules.yaml`
- MCP tool metadata mainly feeds tool order, runtime expectations, and troubleshooting language
- targeted `fs_read` extras should only fill a specific missing fact in one of the buckets above

## Progressive disclosure parameter model

Do not treat the compact parameter guide and full schema coverage as mutually exclusive.

Render both layers:

- compact layer: route-shaping parameters, required inputs, placeholders, restart boundaries, and
  the small set of fields that materially affect ordinary run planning
- full lookup layer: every current schema parameter, grouped into focused files and linked from one
  schema index

The grouped full lookup layer should preserve, at minimum, for each parameter:

- canonical parameter name
- group id
- type
- required status
- default value when present
- enum values when present
- placeholder guidance for path-like or structured fields when useful
- source description or summarized help text
- whether the field belongs in ordinary route planning or only in exact lookup

When choosing groups, prefer categories that help an agent narrow the search quickly:

- the original top-level `nextflow_schema.json` sections named in `allOf`
- the section `title` values carried by the referenced `definitions` or `$defs`
- fallback semantic buckets only when the schema does not expose stable top-level sections

If one pipeline has a clearer source-backed grouping, use that instead. The key rule is that the
schema index must let the runtime agent find the right group without reading the whole schema.

Prefer the schema author's own top-level section ids when they are available through `allOf`. For
example, use `input_output_options`, `reference_genome_options`, `alignment_options`,
`optional_outputs`, or `generic_options` directly as grouped lookup sections.

Only fall back to the older heuristic groups when the schema lacks stable top-level sections:

- `input_paths_and_manifests`
- `references_and_indices`
- `route_selectors_and_booleans`
- `enums_and_choice_params`
- `outputs_and_reporting`
- `tuning_metadata_and_notifications`

For each grouped parameter record, keep at least:

- `name`
- `source_name`
- `type`
- `required`
- `default`
- `enum`
- `description`
- `classification`
- `channel`
- `placeholder`
- `example_values`
- `mapping_notes`
- `lookup_priority`

The generator's default override template lives at
`assets/templates/schema-group-overrides.example.yaml`. Keep pipeline-specific overrides small and
declarative. Do not fork the whole grouping rule set for one or two corrected fields.

Use `classification` to separate route-shaping fields from lookup-only fields and explicit
non-runtime fields. Use `channel` to say whether the field belongs in `params`, `config_files`,
returned runtime metadata, or authoring-only context.

## Runtime tool contract to render into expert skills

Every generated pipeline-specific expert skill should explain the runtime nextmcp subset in compact
form:

- optional `server_info()` checks the current server layout only when the
  runtime still needs a compact readiness summary
- optional `project_list()` discovers the project id when the user has not named it yet
- optional `project_get(project)` confirms the project root or recent runs before launch or reuse
- optional `fs_list(mode="manifest")` confirms one concrete path or output target without a broad
  directory listing
- `nextflow_run(prepare=true)` is the normal pre-launch planning step when input validity, output
  targets, or the historical restart route are still uncertain; generated skills should tell the
  runtime agent to read `run_layout` / `layout_warnings` there when it needs the project-owned run
  root,
  `runs/<run_id>/job`, `runs/<run_id>/work`, or `results/<run_id>`
- `nextflow_run` launches the main pipeline id or an explicit server-local entry script path
- `run_list` narrows historical runs when the user wants to reuse outputs but does not already
  know one concrete server-side path
- `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])` is the first
  post-launch check for summarized state, artifact hints, and failure routing
- `run_get(detail="full")` is the follow-up read when the runtime needs concrete project-owned
  layout paths, `nextflow_log`, or the persisted `run_layout` / `layout_warnings`
- `run_artifacts(...)` reads one artifact section at a time after `run_get(include=["artifact_summary"])`
- `run_logs` reads stdout/stderr or raw Nextflow log lines only after `run_get`
- `fs_read` reads `nextflow_log`, reports, manifests, and named output files
- `nextflow_list_pipelines` is optional and only needed when the runtime must recover a
  server-local `pipeline_dir` to construct an alternate entry-script path

Every generated expert skill should also render the path boundary explicitly:

- all runtime `path` values, the `project` identifier, and relative path-like values in `params`
  or `config_files` refer to the nextmcp server filesystem
- the runtime agent must not pass a client-local path
- placeholder examples should use server-scoped names such as `<server_input_root>/...`

Also render the main parameter-channel boundaries from the tool metadata:

- `params` holds ordinary user-facing pipeline parameters
- `project` is the required project container
- `run_id` is optional when the caller must control the run identifier
- `run_name` is optional when the caller wants a human-readable label
- `config_files` holds Nextflow config files and small server-local override configs
- project-owned layout paths come back through `run_layout` or `run_get(detail="full")`, not as
  public inputs
- `from_run_id` is the only public restart path
- `run_get(detail="full")` on the source run exposes `launch_spec`, `nextflow_session_uuid`, and
  structured resume-compatibility fields used for restart planning
- `extra_args` is only for flags without a normalized field

Render one explicit exception alongside that boundary:

- `max_cpus`, `max_memory`, and `max_time` stay in config scope in the current runtime
- teach the runtime agent to write them into a small server-local override config and pass that
  file through `nextflow_run(config_files=...)`
- do not render those resource caps as ordinary `params`
- inspect the source-backed runtime config shape before choosing the override syntax
- if the pipeline uses `process.resourceLimits` or another config-level key, keep that exact
  structure in the rendered example instead of inventing `params.max_cpus` or `process.maxCpus`

If the pipeline has reusable historical outputs, also render one compact reuse rule:

- prefer `run_list(..., artifact_path_contains=...)` with named path fragments taken from real
  artifact contracts
- use `run_get(include=["artifact_summary"])` plus `run_artifacts(...)` to inspect `artifacts.json`, published roots, items,
  and `pipeline_fingerprint`
- use `pipeline_info/params.json` or equivalent run metadata to confirm the historical route before
  presenting reuse as safe

## Asset-first discipline

Do not hand-write long reference markdown and then backfill assets later. That re-creates the legacy
problem where prose is the only usable source of truth.

Do not render only prose summaries for parameters and leave exact mapping to guesswork. The
schema-backed grouped assets are part of the source-of-truth layer and should be rendered before
the compact parameter references.
