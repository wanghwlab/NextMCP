# Rendering Rules

## Asset rendering

Render expert assets first and keep them concise, structured, and diffable.

Preferred output split:

- `pipeline-profile.yaml`: identity, assumptions, inputs, modes, limitations
- `playbooks.yaml`: scenario routes keyed by user intent
- `step-recipes.yaml`: step-level prerequisites and outputs
- `param-presets.yaml`: reusable parameter bundles
- `schema-index.yaml`: lightweight grouped index into the full current parameter inventory
- `schema-groups/*.yaml`: exact grouped parameter definitions used for progressive disclosure
- `capability-audit.yaml`: high-impact capabilities found during authoring and their coverage status
- `authoring-gaps.yaml`: explicit scaffold gaps that must be resolved or scoped out
- `artifact-contracts.yaml`: downstream handoff files and meanings
- `qc-rules.yaml`: machine-readable QC checks

## Reference rendering

Each reference file should explain one slice of the package:

- scope and assumptions
- playbooks
- parameters
- grouped schema lookup
- outputs and QC
- troubleshooting

Keep the source split visible while rendering:

- parameters and presets should primarily come from `schema`
- playbooks, output review order, QC notes, and troubleshooting should primarily come from
  `documents`
- execution modes, artifact flow, and hidden assumptions should primarily come from `source_files`
- if targeted `fs_read` extras were needed, mention them only where they materially change a route
  or constraint
- if the package was generated from a repository-local pipeline path, say that the authoring source
  was an inspect-equivalent bundle built from `nf_pipeline/<pipeline>` or the concrete repository
  path, not a custom alternate contract

Do not copy raw schema JSON into one monolithic markdown dump. Preserve the full current schema
through grouped assets and grouped references, then summarize the parts that matter for everyday
decision-making in the compact parameter guide.

The compact parameter guide should explain:

- required inputs
- route-shaping parameters
- placeholder conventions
- channel boundaries such as `params` versus `config_files`
- when the runtime agent should escalate from the compact guide to the grouped schema lookup

The grouped schema lookup should preserve exact mapping details without forcing the runtime agent to
read every parameter definition at once.

Prefer a generated grouped schema layer over manual YAML editing:

- use `scripts/generate_schema_groups.py` to create the first draft of `schema-index.yaml`
- use the same script to create `schema-groups/*.yaml`
- use `--write-reference-drafts` only for a first markdown pass; assets remain the primary exact
  source of truth
- keep pipeline-specific grouping fixes in a small override file instead of hand-maintaining every
  grouped schema asset from scratch

Prefer a generated package scaffold over creating every required file by hand:

- use `scripts/scaffold_expert_skill.py` to create the initial expert skill layout and starter
  assets
- treat that scaffold as a minimal draft, not a finished expert skill
- resolve `assets/authoring-gaps.yaml` and every `needs_review` capability before runtime use
- refine playbooks, outputs, QC, and troubleshooting from current docs and source files before
  considering the package complete

Prefer one mixed-source offline eval file over separate eval files:

- write `evals/evals.json` with both asset-derived and source-derived eval items
- use `evals/templates/expert-skill-evals.json` as the starting point when not using the scaffold
  generator
- put `source: asset` on evals that test whether the agent can use packaged assets correctly
- put `source: authoring_bundle` on coverage evals derived from source schema, docs, source files,
  or targeted extras
- put `source: audit` on evals derived from `capability-audit.yaml` or `authoring-gaps.yaml`
- fill `source_materials` with the assets or authoring bundle sections that justify the eval
- keep the prompts focused on planning outputs, coverage, and tool-call shape, not real Nextflow
  execution
- for a one-command local pass, run
  `scripts/run_offline_evals.py --skill-root skills/experts/<pipeline>-expert-skill`;
  add `--agent kimi` when comparing Kimi CLI output with the default Claude run
- use the separate smoke-test contract path when the goal is to prove a run completes and required
  outputs exist

Do not hide significant optional capabilities only in prose. If a current pipeline mode changes
user intent, launch parameters, runtime prerequisites, outputs, or failure modes, render it into
assets first. Typical examples are UMI-aware runs, licensed acceleration, preprocessing-only
routes, contamination screening, build-only entry scripts, assembly-only entries, and extra output
families such as TPM or `SummarizedExperiment`.

If the package intentionally does not cover one of those capabilities, say so explicitly in
limitations or non-scope text. Silent omission is a bug in the generated skill, not a stylistic
choice.

Every generated expert skill should include one compact runtime tool guide. Explain when to use the
runtime nextmcp tools and the main `nextflow_run` parameter boundaries without re-dumping the full
server tool catalog.

That guide should also say that runtime agents should omit `profile` by default and rely on
`server_info().nextflow.default_profile` when runtime environment choice still matters. Only render
explicit `profile` guidance when the user requests a different runtime or the server default is
known to be unsuitable.

When rendering that guide, prefer the smallest useful default route:

- optional `server_info()` only when the runtime still does not know the
  server layout or launch readiness
- optional `project_list()` only when the project id is still unknown
- optional `project_get(project)` only when the runtime needs to confirm the project root or see
  recent runs
- optional `fs_list(mode="manifest")` only when one concrete path needs confirmation
- `nextflow_run(prepare=true)` before launch when inputs, outputs, or the historical restart route
  are still uncertain; when that call appears, tell the runtime agent to inspect `run_layout` /
  `layout_warnings` for the project-owned run root, `runs/<run_id>/job`,
  `runs/<run_id>/work`, and `results/<run_id>`
- `nextflow_run` to launch
- `run_list(..., artifact_path_contains=...)` before artifact reuse when the user remembers a
  likely output name but not the old run id
- `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])` before raw logs
- `run_get(detail="full")` only when the runtime needs concrete project-owned layout paths,
  `nextflow_log`, or the persisted `run_layout` / `layout_warnings`
- `run_artifacts(...)` only after the summary shows the needed artifact section
- `run_logs` only when the summary is not enough
- `fs_read` only for explicit runtime files

Every generated expert skill should also include one compact path-boundary rule:

- all runtime `path` values, the `project` identifier, and relative path-like values in `params`
  or `config_files` are resolved on the nextmcp server filesystem
- do not use ambiguous bare `local path` wording; prefer `server-local path`
- use server-scoped placeholders such as `<server_input_root>/...` unless the user or a tool call
  already provided a concrete server path

When a reference includes concrete nextmcp call examples:

- use current tool names
- use runtime examples first: `nextflow_run(prepare=true)` when planning still matters,
  `nextflow_run` to launch, `run_list(..., artifact_path_contains=...)` for historical
  artifact recovery when needed, `run_get(include=[...])` before `run_artifacts(...)` or
  `run_logs`, and `fs_read` for `nextflow_log` or explicit output files
- do not imply that the default `run_get(include=[...])` summary already exposes
  project-owned layout paths, `nextflow_log`, `run_layout`, or other detail-only fields; use
  `run_get(detail="full")` only when those fields are actually needed
- omit `profile` in examples unless the example is specifically about overriding the server default
- keep `server_info()` and `fs_list(mode="manifest")` optional in examples;
  they should appear when uncertainty exists, not as unconditional boilerplate
- use `nextflow_list_pipelines` only when the runtime needs a server-local pipeline root to
  construct an alternate entry-script path
- keep `nextflow_inspect_pipeline` out of ordinary runtime playbooks; if needed, mention it only as
  authoring-time provenance
- keep resource-cap examples honest: `max_cpus`, `max_memory`, and `max_time` should appear in a
  small override config passed through `config_files`, not as ordinary `params`
- preserve the pipeline's own config syntax for that override; if the source materials use
  `process.resourceLimits`, keep `process.resourceLimits` in the example instead of switching to
  `params.max_cpus` or `process.maxCpus`
- do not teach project-owned layout paths as public inputs; teach `project` as the required run
  container and use `run_layout` or `run_get(detail="full")` when concrete paths are needed
- do not bring back removed names such as `nextflow_get_schema` or `nextflow_get_pipeline`

When rendering the progressive disclosure parameter layer:

- keep `references/03_parameters.md` as the compact route-shaping guide
- add one grouped schema overview reference that explains how the parameter index is organized
- add grouped parameter references that mirror the `schema-groups/*.yaml` assets
- make the schema index the only place that needs to know the full group map
- make every grouped reference focused enough that the runtime agent can load one group for exact
  lookup instead of scanning the whole parameter surface
- prefer the schema author's own top-level `allOf` section ids and the referenced `definitions` or
  `$defs` titles when the current schema exposes that structure
- use the fallback heuristic group ids from the extraction rules only when the schema does not
  expose a stable top-level section layout
- include the current schema field name, type, required status, defaults, enum choices, and short
  source-backed descriptions in the grouped assets or grouped references
- include `classification`, `channel`, placeholder guidance, and mapping notes in the grouped
  assets so exact mapping does not depend on prose interpretation
- include `confidence` and `mapping_flags`; when a field is an object, array, `oneOf`, or `anyOf`,
  keep `needs_exact_lookup` visible so the runtime agent knows not to trust a compact summary alone
- avoid duplicating long prose in both grouped assets and grouped references; keep the assets as the
  primary exact source and let the grouped references stay concise

When rendering historical artifact reuse guidance:

- prefer exact filenames or subpaths already present in `artifact-contracts.yaml`
- mention `artifacts.json` and `pipeline_fingerprint` as facts returned by
  `run_get(include=["artifact_summary"])` plus `run_artifacts(...)`
- require route confirmation through `pipeline_info/params.json` or an equivalent metadata file
- do not present broad history scans or guessed outdirs as the default safe path

When a pipeline ships alternate entry scripts or step-local workflows:

- list the major entries in `pipeline-profile.yaml` supported modes
- add explicit recipes for build-only, assembly-only, or QC-only entries when they affect planning
- do not collapse them into a generic "interactive mode" sentence if the required inputs differ

## `SKILL.md` rendering

Keep `SKILL.md` as an entrypoint:

- short frontmatter with strong trigger wording
- explicit scope and non-scope
- list of authoritative assets
- pointer map into references
- one compact runtime tool contract
- one compact path-boundary rule
- one short pointer to the compact parameter guide plus the grouped schema lookup path
- short operating rules and fast-start playbooks
