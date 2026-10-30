---
name: pipeline-expert-skill-creator
description: >-
  Use whenever the user wants to create, revise, evaluate, or regenerate a
  `<pipeline>-expert-skill` from a nextmcp server's pipeline materials or
  directly from a repository-local pipeline checkout such as
  `nf_pipeline/rnaseq` or `nf_pipeline/riboseq`. Trigger even when the user
  only mentions a pipeline ID already configured on the nextmcp server, a
  pipeline source path, `nextflow_inspect_pipeline`, schema/doc changes,
  workflow updates, or asks to turn pipeline docs and code into an installable
  expert skill package.
compatibility: >-
  Requires either a nextmcp MCP server with current tool docstrings/input
  schemas plus `server_info`, `project_list`, `project_get`, `fs_list`,
  `nextflow_list_pipelines`, `nextflow_inspect_pipeline`, `nextflow_run`,
  `run_list`, `run_get`, `run_artifacts`, `run_logs`, and `fs_read`, or a
  repository checkout that contains the current pipeline source tree such as
  `nf_pipeline/<pipeline>/`, plus access to the repository skill templates and
  validation files.
metadata:
  skill-class: meta
  tool-surface: nextmcp
  tool-surface-version: "2026-03-15"
  generated-from: docs-skills-design-spec
---

# Pipeline Expert Skill Creator

## Scope

Create and maintain repository-side expert skill source packages from nextmcp-returned pipeline
materials or repository-local inspect-equivalent bundles built from vendored pipeline trees and
repository templates. Use this together with the general-purpose `skill-creator` skill when
actually creating or iterating an expert skill package. `skill-creator` owns the generic authoring
and evaluation loop; this skill supplies the nextmcp- and pipeline-specific rules for collecting
authoring materials, extracting facts, rendering assets, and validating the final package. Keep
creation-time collection tools separate from the runtime tool surface that the generated expert
skill teaches to the agent.

## When to use this skill

Use this skill when the user wants to build a new expert skill, refresh an existing one after
pipeline changes, migrate legacy markdown into asset-backed packages, or validate that a skill
source package still follows the repository contract.

## What this skill does not handle

- replacing the general-purpose `skill-creator` eval and iteration workflow
- treating legacy skills as the final source of truth
- hiding pipeline expertise in scripts while leaving assets incomplete
- registering skills in the `nextmcp` server runtime

## Authoring material map

- `nextflow_list_pipelines` is only for discovery when the server-visible pipeline ID is not
  already known.
- `nextflow_inspect_pipeline(detail="materials")` is the default single-call source collector for
  one pipeline during authoring. `detail="summary"` is only for small manifests or quick checks.
- If the pipeline is only available as a repository-local checkout such as `nf_pipeline/rnaseq` or
  `nf_pipeline/riboseq`, build the same authoring bundle shape that
  `nextflow_inspect_pipeline(detail="materials")` returns:
  `schema`, `documents`, and `source_files`.
- When building that repository-local bundle, keep the same descriptor keys and roles used by
  `src/nextmcp/nextflow_catalog.py`: `documents` use `readme` for `README.md` and `doc` for
  top-level `docs/*.md`; `source_files` use `main_script` for `main.nf`,
  `nextflow_config` for `nextflow.config`, `entry_script` for top-level `*.nf` files other than
  `main.nf`, and `workflow_script` for top-level `workflows/*.nf`.
- Repository-local authoring should stay aligned with the server's standard inspect payload, not a
  broader ad hoc file dump. Nested workflow files such as `workflows/rnaseq/main.nf` and deeper
  docs pages such as `docs/usage/differential_expression_analysis/*.md` are still targeted extras,
  not part of the standard bundle.
- Treat `schema` as the current parameter contract: required inputs, defaults, enums, and preset
  candidates.
- Treat `documents` as README plus top-level docs for user scenarios, output review order, QC
  interpretation, and troubleshooting.
- Treat `source_files` as the current execution contract: `main.nf`, `nextflow.config`,
  `workflow_script`, and `entry_script` content reveal modes, step boundaries, published
  artifacts, and assumptions that docs may summarize loosely.
- Use `fs_read` only for targeted extras that are not already in the standard inspect payload, such
  as deeper docs pages or nested workflow files. For example, `nf_pipeline/rnaseq/workflows/rnaseq/main.nf`
  and `docs/usage/differential_expression_analysis/*.md` may still need targeted reads even after
  inspection.
- When docs or schema reveal a high-impact optional mode but the runtime shape is still unclear,
  use targeted reads of tests, nested workflows, or alternate entry scripts to confirm the real
  prerequisites, outputs, and failure modes.

## Authoritative assets

- `assets/extraction-rules.yaml`
- `assets/asset-schema.yaml`
- `assets/schema-grouping-rules.yaml`
- `assets/validation-checklist.yaml`
- `assets/templates/expert-skill-layout.yaml`
- `assets/templates/frontmatter.yaml`
- `assets/templates/schema-group-overrides.example.yaml`
- `evals/templates/expert-skill-evals.json`

## References to read next

- `references/01_source_inventory.md`
- `references/02_extraction_workflow.md`
- `references/03_rendering_rules.md`
- `references/04_validation.md`

## Helper scripts

- `scripts/build_authoring_bundle.py`: build a repository-local inspect-equivalent bundle from
  `nf_pipeline/<pipeline>` using the same collection rules as `nextflow_inspect_pipeline`
- `scripts/scaffold_expert_skill.py`: turn one authoring bundle into a minimal editable expert
  skill package draft
- `scripts/generate_schema_groups.py`: generate the grouped schema lookup layer from
  `nextflow_schema.json`
- `scripts/audit_capabilities.py`: scan one authoring bundle for high-impact modes, outputs,
  prerequisites, alternate entries, and other items that must be covered or scoped out
- `scripts/validate_expert_skill.py`: run machine-checkable package validation after assets are
  filled in
- `scripts/run_offline_evals.py`: run one generated expert skill's `evals/evals.json` prompts
  through `claude`, `codex`, `kimi`, or `mock`, and save outputs, timing, grading, and summary
  files
- `evals/templates/expert-skill-evals.json`: seed `skill-creator` offline evals for generated
  expert skills; these evals test planning and tool-call shape and do not launch Nextflow

## Operating rules

- Use the `skill-creator` skill as the main skill-authoring workflow when creating or revising an
  expert skill package.
- Treat this skill as the domain-specific rule set layered on top of `skill-creator`, not as a
  replacement for it.
- Use the default authoring sequence: collect or build the authoring bundle, generate schema
  groups, run capability audit, scaffold the package, fill or scope out audit gaps in assets, run
  the validator, then use `skill-creator` with the offline eval template for eval and iteration.
- Keep creation-time collection tools separate from runtime tools in the generated expert skill.
- Start from `nextflow_inspect_pipeline(detail="materials")` when a live nextmcp server is
  available. If the user gives a repository path such as `nf_pipeline/rnaseq`, first normalize that
  directory into the same authoring bundle shape before extracting facts.
- Use `nextflow_list_pipelines` only when the pipeline ID is unknown; otherwise go straight to
  `nextflow_inspect_pipeline(detail="materials")` or to the known repository-local pipeline path.
- When authoring from repository files, keep the same top-level bundle keys and asset descriptor
  shape as the inspect payload: `schema`, `documents`, `source_files`, and each file entry as
  `{"role": "...", "path": "...", "content": "..."}`.
- When authoring from repository files, keep the standard bundle narrow. Do not silently pull in
  nested `docs/**` or `workflows/**` files that the server would not inline by default.
- Build the structured model in this order: `source_files`, `schema`, `documents`, MCP tool
  metadata, then any targeted `fs_read` extras.
- Treat repository-local inspect-equivalent materials and
  `nextflow_inspect_pipeline(detail="materials")` as the same source tier once they are normalized
  to the same shape.
- Turn `schema` facts into presets, parameter boundaries, placeholder guidance, and a complete
  schema-backed parameter reference split for progressive disclosure.
- Do not leave the generated expert skill with only a partial parameter summary when correct
  parameter mapping depends on current `nextflow_schema.json` details.
- Do not paste raw `nextflow_schema.json` as one large unreadable blob. Preserve the full schema
  content through structured parameter assets and references that let the runtime agent discover
  detailed fields progressively.
- Treat the following as the default parameter-selection heuristic, not a fixed allowlist:
  required inputs and common core references for normal runs; booleans, enums, and common options
  that materially change route choice, runtime prerequisites, outputs, QC interpretation,
  historical reuse safety, or common failure modes; and nextmcp boundary params that must be put in
  the right channel, such as `params` versus `config_files`, historical restart via
  `from_run_id`, and default-profile handling.
- Generated expert skills should keep two parameter layers:
  a compact route-shaping layer for everyday planning, plus a complete schema-backed layer for
  exact parameter lookup when the runtime agent must map or verify a specific field.
- Organize the complete schema-backed layer for progressive disclosure:
  one lightweight schema index asset, one overview reference, and grouped parameter files keyed first by the
  original top-level `nextflow_schema.json` section structure from `allOf` plus the referenced
  `definitions` or `$defs`. When that structure is unavailable or not stable, fall back to grouped
  categories such as input paths, references, booleans and route selectors, enums and choice
  parameters, resource-adjacent pipeline params, and output or reporting params.
- Use `scripts/generate_schema_groups.py` as the default v1 generator for that grouped schema
  layer when starting from `nextflow_schema.json`; use
  `assets/templates/schema-group-overrides.example.yaml` only for pipeline-specific corrections
  that the default grouping heuristics cannot infer safely.
- Prefer the schema author's own top-level section ids such as `input_output_options`,
  `reference_genome_options`, `alignment_options`, `umi_options`, or `generic_options` when the
  current schema exposes them through `allOf`. Use the older heuristic groups only as a fallback
  for schemas that do not expose stable top-level sections.
- Parameter groups may be refined per pipeline when a source-backed structure is clearer, but every
  current schema parameter must appear in exactly one group or in one explicit non-runtime bucket
  with a reason.
- Parameters that are mainly for notifications, presentation, profile metadata, generic validation
  toggles, or low-impact internal tuning usually do not belong in the main compact parameter guide
  unless real user requests depend on them or they materially change runtime behavior.
- Those lower-impact parameters should still be preserved in the complete schema-backed layer with
  their type, default, enum choices when present, required status, and source description.
- Each grouped parameter record should preserve enough detail for exact mapping: canonical name,
  group id, JSON-schema type or normalized type, required status, default, enum choices when
  present, description, placeholder guidance when useful, example values when useful, and whether
  the field is route-shaping, lookup-only, or non-runtime. It should also expose a confidence value
  and mapping flags such as `needs_exact_lookup` for complex object, array, `oneOf`, or `anyOf`
  fields.
- If a parameter is omitted from the main compact parameter guide but a supported mode depends on
  it, cover that mode through presets, playbooks, step recipes, artifact contracts, QC rules, or
  the grouped schema reference, or explicitly scope it out.
- Turn `documents` facts into playbooks, output review order, QC notes, and troubleshooting routes.
- Turn `source_files` facts into execution modes, step recipes, and artifact contracts.
- Sweep the current materials for significant optional capabilities that materially change route
  choice, runtime prerequisites, outputs, or interpretation. Examples include `with_umi`,
  `use_sentieon_star`, preprocessing-only switches such as `skip_alignment` plus
  `skip_pseudo_alignment`, contamination routes such as `kraken2_bracken`, alternate entry scripts
  such as `STEP_BUILD_STAR_INDEX`, and special outputs such as `STEP_ASSEMBLE_STRINGTIE`.
- Use `scripts/audit_capabilities.py` as the default first pass for this sweep. Treat each
  `needs_review` item in `assets/capability-audit.yaml` as an explicit todo until it is either
  covered in the listed assets or marked `scoped_out` with a reason.
- Every significant optional capability must be covered in structured assets and references, or be
  explicitly scoped out in the generated expert skill with a clear reason. Do not silently drop it.
- If `nextflow_inspect_pipeline` does not include a file that materially changes workflow behavior,
  fetch only that file with `fs_read` and note why it was needed.
- Generated expert skills should expose full current-schema coverage through progressive disclosure
  without forcing the runtime agent to load every parameter definition at once.
- Generated expert skills should point the runtime agent first to the compact route-shaping guide,
  then to the schema index, then to the matching grouped parameter file when exact mapping or value
  validation is needed.
- Generated expert skills must say explicitly that all runtime `path` values, the `project`
  identifier, and relative path-like values in `params` or `config_files` are resolved on the
  nextmcp server filesystem, not on the client machine.
- Generated expert skills must tell the runtime agent to use only paths returned by nextmcp tools
  or paths the user already confirmed exist on the server.
- Generated expert skills should use server-scoped placeholder paths such as
  `<server_input_root>/...` instead of bare `/data`, `/results`, or other ambiguous examples,
  unless they are echoing a concrete server path confirmed by the user.
- Generated expert skills must teach the runtime nextmcp subset they actually use:
  optional `server_info()` when the runtime layout is still unknown,
  optional `project_list()` when the project id is still unknown,
  optional `project_get(project)` when the runtime needs to confirm the project root or inspect
  recent runs,
  optional `fs_list(mode="manifest")` when one concrete server path needs confirmation,
  `nextflow_run(prepare=true)` before launch when inputs or target outputs still need checking,
  with `run_layout` / `layout_warnings` used to confirm the project-owned run root,
  `runs/<run_id>/job`, `runs/<run_id>/work`, and `results/<run_id>`,
  `nextflow_run` to launch work, `run_list` when historical runs must be recovered,
  `run_get(include=[...])` to inspect state and summarize progress or failures,
  `run_artifacts(...)` to inspect artifact sections,
  `run_logs` only for raw stdout/stderr or Nextflow log lines, `fs_read` for explicit logs or
  outputs, and `nextflow_list_pipelines` only when a server-local pipeline root is needed to
  construct an alternate entry-script path.
- Do not tell the runtime agent to start ordinary planning or execution with
  `nextflow_inspect_pipeline`. That tool belongs to skill creation and package maintenance, not the
  default runtime playbooks of a generated pipeline-specific expert skill.
- Generated expert skills must explain the main `nextflow_run` channel boundaries from the current
  MCP tool docstrings: `params` for ordinary pipeline-facing options such as inputs, references,
  route selectors, and tool-specific `extra_*` params; required `project` for the server-side
  project container; optional `run_id` / `run_name` for run identity; `config_files` for Nextflow
  config files and small server-local override configs; `from_run_id` as the only public restart
  path; and `extra_args` only when no normalized field already covers the needed CLI flag.
- Generated expert skills must teach runtime agents to inspect `run_get(detail="full")` on the
  source run when restart planning matters, because that view returns `launch_spec`,
  `nextflow_session_uuid`, and structured resume-compatibility fields.
- Generated expert skills must not teach `resume` or `resume_session_id` as public
  `nextflow_run` inputs.
- Generated expert skills must teach runtime agents that resource-cap settings such as
  `max_cpus`, `max_memory`, and `max_time` stay in config scope in the current runtime. Put them in
  a small server-local override config and pass that file through `nextflow_run(config_files=...)`,
  not through `nextflow_run(params=...)`.
- Generated expert skills must preserve the pipeline's own resource-override syntax instead of
  inventing a generic one. Inspect the current `nextflow.config`, profile config, and other
  source-backed runtime materials before rendering examples. If the source uses
  `process.resourceLimits` or another config-level key, keep that exact structure in the rendered
  override example. For example, `riboseq` should render
  `process { resourceLimits = [cpus: ..., memory: '...', time: '...'] }`, not `params.max_cpus`
  and not `process.maxCpus`.
- Generated expert skills must teach runtime agents to omit `profile` by default and rely on
  `server_info().nextflow.default_profile` when runtime environment selection still matters.
  They should only pass `profile` explicitly when the user requests a different runtime or the
  server default is known to be unsuitable.
- Keep `fs_read` split clear: during authoring it is a targeted fallback for missing source
  materials; during runtime it is a targeted reader for `nextflow_log`, reports, manifests, and
  named output files after their paths are known.
- Generated expert skills should prefer summarized runtime reads first:
  `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])` before raw logs and
  `fs_list(mode="manifest")` before broad directory scans.
- If generated runtime guidance needs concrete project-owned layout paths, `nextflow_log`, or the
  persisted `run_layout` / `layout_warnings`, render them as follow-up reads from
  `run_get(detail="full")`, `run_logs`, or artifact metadata, not as part of the default summary
  payload.
- When a pipeline publishes reusable historical outputs, generated expert skills must teach the
  runtime agent to recover prior runs with `run_list(..., artifact_path_contains=...)` before
  reading `run_get(include=["artifact_summary"])` plus `run_artifacts(...)`.
- Generated expert skills should prefer path fragments grounded in known artifact contracts, such
  as `pipeline_info/params.json`, a BAM-aware samplesheet, or a report filename, instead of broad
  history scans when the user only remembers one output name.
- Generated expert skills must teach the runtime agent to treat `artifacts.json` and
  `pipeline_fingerprint` as historical facts, then confirm compatibility through
  `pipeline_info/params.json` or equivalent run metadata before presenting reuse as the default
  safe path.
- When a pipeline ships alternate entry workflows, build-only steps, or assembly-only steps, expose
  them as supported modes or step recipes instead of leaving them buried in prose.
- Extract structured facts first, then render prose.
- Resolve source conflicts by the priority order in `assets/extraction-rules.yaml`.
- Run `scripts/validate_expert_skill.py` after filling the generated assets. Treat failed machine
  checks as blockers and treat `manual_review` checks as explicit review work, not as passing
  validation.
- Use `evals/templates/expert-skill-evals.json` to create the first offline eval set for the
  generated expert skill. Replace placeholders with source-backed pipeline terms and keep these
  evals offline unless the user explicitly asks to run a real Nextflow smoke test.
- Use `scripts/run_offline_evals.py` when the user wants a one-command local run of a generated
  expert skill's offline `evals/evals.json`. Treat its rule-based grading as a first pass; use
  human or reviewer-agent feedback for semantic quality.
- Keep expert skills focused on user-intent playbooks, presets, artifacts, and QC interpretation.
- Keep final packages client-side and out of the `nextmcp` runtime dependency graph.

## Fast-start playbooks

1. New pipeline on a nextmcp server: discover the ID if needed, inspect the pipeline, generate
   schema groups and capability audit, scaffold the package, fill assets, validate, then run
   offline skill evals.
2. Pipeline is only available in the repository, for example `nf_pipeline/rnaseq` or
   `nf_pipeline/riboseq`: build the inspect-equivalent authoring bundle from that directory first,
   then run the same schema grouping, capability audit, scaffold, fill, validate, and eval flow.
3. Existing expert skill drifted after schema, docs, or workflow changes: rerun
   `nextflow_inspect_pipeline(detail="materials")` or rebuild the repository-local equivalent,
   refresh structured assets from `schema` / `documents` / `source_files`, then rewrite references
   from those assets instead of editing prose in place.
4. Pipeline keeps key logic outside the standard inspect payload: use targeted `fs_read` or direct
   repository reads for the missing nested workflow or deeper docs file, then fold that material
   back into the same asset model.
5. Need to validate a package before client install: run `scripts/validate_expert_skill.py`, then
   use `references/04_validation.md` for the remaining manual checks.
