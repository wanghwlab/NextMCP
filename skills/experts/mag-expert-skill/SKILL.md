---
name: mag-expert-skill
description: Use when the user wants to plan, run, interpret, or troubleshoot nf-core/mag
  analyses through nextmcp, including short-read, long-read, hybrid, pre-computed assembly,
  ancient DNA, bin QC, taxonomy, annotation, BIgMAG, exact parameter lookup, or reruns.
compatibility: Requires access to nextmcp tool docstrings plus server_info, project_list,
  project_get, fs_list, nextflow_run, run_list, run_get, run_artifacts, run_logs,
  fs_read, and nextflow_list_pipelines only when a server-local pipeline root is needed.
metadata:
  skill-class: expert
  pipeline-id: mag
  pipeline-version: 5.4.2
  generated-from: authoring bundle rooted at /root/key_projects/nextmcp/nf_pipeline/mag
---

# nf-core/mag Expert Skill

## Release and launch selection

This package targets **nf-core/mag 5.4.2**. For a new remote run, use
`pipeline="nf-core/mag"` with `extra_args=["-r", "5.4.2"]`. Short pipeline
IDs in historical recipes require a matching configured local catalogue; do not assume
they resolve in a remote-only deployment. For a restart, use `from_run_id` and omit
`project`, `pipeline`, and `run_id`; inspect the stored launch specification first.

## Scope

Expert skill for planning, launching, reviewing, and troubleshooting `nf-core/mag` through
nextmcp. It covers metagenome assembly, binning, bin quality checks, taxonomic classification,
genome annotation, ancient DNA validation, virus identification, BIgMAG summary output, and
pre-computed assembly input.

## What this skill does not handle

- biological interpretation beyond the pipeline's documented reports and tables
- server setup, pipeline installation, container policy, or database staging
- raw-read taxonomic profiling; nf-core/mag removed that feature in version 5.0.0
- ordinary runtime planning through `nextflow_inspect_pipeline`; that was only used to create this
  package

## When to use this skill

Use this skill when a user asks to plan, launch, review, rerun, or troubleshoot `nf-core/mag`
through nextmcp, or when they need exact schema-backed parameter lookup for this pipeline.

## Authoritative assets

- `assets/pipeline-profile.yaml`: scope, modes, assumptions, resource override syntax, and
  server-local path rule.
- `assets/playbooks.yaml`: user-intent routes and runtime tool order.
- `assets/step-recipes.yaml`: launch, pre-computed assembly, database, ancient DNA, review, and
  historical reuse recipes.
- `assets/param-presets.yaml`: reusable parameter bundles and nextmcp channel placement.
- `assets/schema-index.yaml`: map from parameter names and schema groups to exact lookup files.
- `assets/schema-groups/*.yaml`: complete current-schema parameter definitions.
- `assets/artifact-contracts.yaml`: output families, reuse paths, and review order.
- `assets/qc-rules.yaml`: QC signals and next actions.
- `assets/capability-audit.yaml`: source-backed coverage record for high-impact capabilities.
- `assets/authoring-gaps.yaml`: resolved authoring items.

## References to read next

- `references/01_scope_and_assumptions.md`: scope, source basis, modes, and limits.
- `references/02_playbooks.md`: route narratives and workflow choices.
- `references/03_parameters.md`: compact parameter guide and `params` versus `config_files`.
- `references/04_schema_lookup.md`: how to use the grouped schema assets.
- `references/05_outputs_and_qc.md`: output review order and QC interpretation.
- `references/06_troubleshooting.md`: common failure routes and recovery steps.

## Operating rules

- Use packaged assets first. Do not call `nextflow_inspect_pipeline` during ordinary runtime planning.
- All runtime `path` values, the `project` identifier, and relative path-like values in `params`
  or `config_files` resolve on the nextmcp server filesystem, not on the client machine.
- Use only paths returned by nextmcp tools or paths the user confirmed already exist on the
  server. Do not pass a client-local path unless the user confirms the same path exists on the
  server. Use placeholders such as `<server_input_root>/samplesheet.csv` when drafting.
- Put pipeline-facing options in `nextflow_run(params=...)`: input, outdir, assembly_input, route
  selectors, database paths, skip/save toggles, and tool-specific options.
- Put Nextflow config files and resource caps in `nextflow_run(config_files=[...])`. For this
  pipeline, resource caps should use `process { resourceLimits = [...] }`; do not invent
  `params.max_cpus`, `params.max_memory`, `params.max_time`, or `process.maxCpus`.
- Omit `profile` by default and rely on the server default profile unless the user asks for a
  different runtime or the server default is known to be unsuitable.
- Use `from_run_id` as the public restart path. Read `run_get(detail="full")` on the source run
  when `launch_spec`, `nextflow_session_uuid`, or `resume_compatible` matters. Do not teach direct
  Nextflow resume flags as public `nextflow_run` inputs.
- After launch, use `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`
  before `run_artifacts`, `run_logs`, or `fs_read`.

## Fast-start playbooks

1. Read `assets/playbooks.yaml` and choose the route.
2. Read `references/03_parameters.md` for required placeholders and nextmcp channel placement.
3. Use `assets/schema-index.yaml` and one `assets/schema-groups/*.yaml` file when exact type,
   default, enum, or mapping detail matters.
4. Use `assets/artifact-contracts.yaml` and `assets/qc-rules.yaml` after the run reports outputs.
