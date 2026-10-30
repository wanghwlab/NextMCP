---
name: ampliseq-expert-skill
description: Use when the user wants to plan, run, interpret, or troubleshoot nf-core/ampliseq analyses through nextmcp, including Illumina, PacBio, IonTorrent, ITS, multi-region Sidle, DADA2, SINTAX, Kraken2, QIIME2, pplacer, ANCOM, ANCOM-BC, PICRUSt2, SBDI export, exact parameter lookup, output review, or reruns.
compatibility: Requires access to the nextmcp tool docstrings plus server_info, project_list, project_get, fs_list, nextflow_run, run_list, run_get, run_artifacts, run_logs, fs_read, and nextflow_list_pipelines when the runtime needs a server-local pipeline path.
metadata:
  skill-class: expert
  pipeline-id: ampliseq
  pipeline-version: 2.16.1
  generated-from: authoring bundle rooted at /root/key_projects/nextmcp/nf_pipeline/ampliseq
---

# nf-core/ampliseq Expert Skill

## Release and launch selection

This package targets **nf-core/ampliseq 2.16.1**. For a new remote run, use
`pipeline="nf-core/ampliseq"` with `extra_args=["-r", "2.16.1"]`. Short pipeline
IDs in historical recipes require a matching configured local catalogue; do not assume
they resolve in a remote-only deployment. For a restart, use `from_run_id` and omit
`project`, `pipeline`, and `run_id`; inspect the stored launch specification first.

## Scope

Expert skill for planning, launching, reviewing, and troubleshooting `nf-core/ampliseq` through
nextmcp. It covers the main amplicon workflow, the three input routes (`input`, `input_folder`,
and `input_fasta`), sequencing-platform switches, ITS handling, multi-region Sidle analysis,
taxonomy alternatives, metadata-driven downstream analysis, major output families, and reruns.

## What this skill does not handle

- biological interpretation beyond the pipeline's documented outputs
- server setup, pipeline installation, or container/runtime policy decisions
- ordinary runtime planning through `nextflow_inspect_pipeline`; that was only used to create this
  package

## Authoritative Assets

- `assets/pipeline-profile.yaml`: scope, modes, assumptions, resource override syntax, and
  server-local path boundary.
- `assets/playbooks.yaml`: user-intent routes and runtime tool order.
- `assets/step-recipes.yaml`: main launch, restart, and historical-output recipes.
- `assets/param-presets.yaml`: reusable parameter bundles and nextmcp channel boundaries.
- `assets/schema-index.yaml`: map from parameter names and schema groups to exact lookup files.
- `assets/schema-groups/*.yaml`: complete current-schema parameter definitions.
- `assets/artifact-contracts.yaml`: output families, reuse paths, and review order.
- `assets/qc-rules.yaml`: QC signals and next actions.
- `assets/capability-audit.yaml`: source-backed coverage record for high-impact capabilities.
- `assets/authoring-gaps.yaml`: resolved and scoped-out authoring items.

## References

- `references/01_scope_and_assumptions.md`: scope, source basis, and limits.
- `references/02_playbooks.md`: route narratives and workflow choices.
- `references/03_parameters.md`: compact parameter guide and `params` versus `config_files`.
- `references/04_schema_lookup.md`: how to use the grouped schema assets.
- `references/05_outputs_and_qc.md`: output review order and QC interpretation.
- `references/06_troubleshooting.md`: common failure routes and recovery steps.

## Runtime Rules

- Use packaged assets first. Do not start normal runtime planning with `nextflow_inspect_pipeline`.
- If a request depends on a missing, stale, or unresolved authoring item, read
  `assets/authoring-gaps.yaml` and the relevant packaged asset, then either use the packaged
  coverage, state the limit, or scope out the request with a reason. In that answer, name
  `assets/authoring-gaps.yaml` explicitly so the limit is traceable.
- Do not recommend `nextflow_inspect_pipeline` or source-tree `publishDir` review as runtime
  fallback steps.
- All runtime `path` values, the `project` identifier, and relative path-like values in `params`
  or `config_files` resolve on the nextmcp server filesystem, not on the client machine.
- Use only paths returned by nextmcp tools or paths the user confirmed already exist on the
  server. Use placeholders such as `<server_input_root>/samplesheet.tsv` when drafting.
- Put pipeline-facing options in `nextflow_run(params=...)`: `input`, `input_folder`,
  `input_fasta`, primers, metadata, taxonomy choices, sequencing-platform switches,
  downstream-analysis switches, and skip/save toggles.
- Use exactly one primary input route unless a documented mode says otherwise: `input`,
  `input_folder`, or `input_fasta`.
- Put Nextflow config files and resource caps in `nextflow_run(config_files=[...])`. For this
  pipeline, resource caps should use `process { resourceLimits = [...] }`; do not invent
  `params.max_cpus`, `params.max_memory`, `params.max_time`, or `process.maxCpus`.
- Omit `profile` by default and rely on the server default profile unless the user asks for a
  different runtime or the server default is known to be unsuitable.
- Use `from_run_id` as the public restart path. Read `run_get(detail="full")` on the source run
  when `launch_spec`, `nextflow_session_uuid`, or resume compatibility matters. Do not teach
  raw Nextflow resume flags as public `nextflow_run` inputs.
- After launch, use `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`
  before `run_artifacts`, `run_logs`, or `fs_read`.

## Fast Start

1. Read `assets/playbooks.yaml` and choose the route.
2. Read `references/03_parameters.md` for required placeholders and nextmcp channel boundaries.
3. Use `assets/schema-index.yaml` and one `assets/schema-groups/*.yaml` file when exact type,
   default, enum, or mapping detail matters.
4. Use `assets/artifact-contracts.yaml` and `assets/qc-rules.yaml` after the run reports outputs.
