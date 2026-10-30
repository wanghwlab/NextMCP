---
name: rnaseq-expert-skill
description: Use when the user wants to plan, run, interpret, or troubleshoot nf-core/rnaseq analyses through nextmcp, including FASTQ or pipeline-generated BAM input, STAR-Salmon, STAR-RSEM, HISAT2, Salmon or Kallisto pseudoalignment, UMI handling, rRNA removal, BBSplit, Kraken2/Bracken contamination screening, StringTie, exact parameter lookup, or reruns.
compatibility: Requires access to nextmcp tool docstrings plus server_info, project_list, project_get, fs_list, nextflow_run, run_list, run_get, run_artifacts, run_logs, fs_read, and nextflow_list_pipelines when the runtime needs a server-local path for interactive.nf.
metadata:
  skill-class: expert
  pipeline-id: rnaseq
  pipeline-version: 3.22.2
  generated-from: authoring bundle rooted at /root/key_projects/nextmcp/nf_pipeline/rnaseq
---

# nf-core/rnaseq Expert Skill

## Release and launch selection

This package targets **nf-core/rnaseq 3.22.2**. For a new remote run, use
`pipeline="nf-core/rnaseq"` with `extra_args=["-r", "3.22.2"]`. Short pipeline
IDs in historical recipes require a matching configured local catalogue; do not assume
they resolve in a remote-only deployment. For a restart, use `from_run_id` and omit
`project`, `pipeline`, and `run_id`; inspect the stored launch specification first.

## Scope

Expert skill for planning, launching, reviewing, and troubleshooting `nf-core/rnaseq` through
nextmcp. It covers the main RNA-seq workflow, FASTQ samplesheets, the pipeline's BAM reprocessing
workflow, STAR-Salmon, STAR-RSEM, HISAT2, optional Salmon or Kallisto pseudoalignment, UMI-aware
runs, BBSplit genome filtering, SortMeRNA rRNA removal, Sentieon STAR acceleration,
Kraken2/Bracken contamination screening, StringTie, MultiQC, and exact parameter lookup.

## What this skill does not handle

- biological interpretation beyond the pipeline's documented QC and output files
- server setup, pipeline installation, container policy, or Nextflow secret creation
- ordinary runtime planning through `nextflow_inspect_pipeline`; that tool was only used to create
  this package
- arbitrary BAM reprocessing outside the documented two-step workflow from this same pipeline

## Authoritative Assets

- `assets/pipeline-profile.yaml`: scope, modes, assumptions, resource override syntax, and
  server-local path boundary.
- `assets/playbooks.yaml`: user-intent routes and runtime tool order.
- `assets/step-recipes.yaml`: main, restart, and `interactive.nf` step recipes.
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

- The `interactive.nf` / `STEP_*` route is an optional custom extension from the
  historical authoring checkout. It is not shipped here and is not guaranteed by
  an official remote release. Use it only when the user requests it and the server
  confirms the matching script and entry are installed; otherwise scope it out.

- Use packaged assets first. Do not start normal runtime planning with `nextflow_inspect_pipeline`.
- All runtime `path` values, the `project` identifier, and relative path-like values in `params`
  or `config_files` resolve on the nextmcp server filesystem, not on the client machine.
- Use only paths returned by nextmcp tools or paths the user confirmed already exist on the
  server. Use placeholders such as `<server_input_root>/samplesheet.csv` and
  `<server_output_root>/rnaseq` when drafting.
- Put pipeline-facing options in `nextflow_run(params=...)`: `input`, `outdir`, reference files,
  alignment route selectors, UMI settings, BBSplit and rRNA settings, contamination screening,
  skip switches, and save switches.
- Put Nextflow config files and resource caps in `nextflow_run(config_files=[...])`. For this
  pipeline, the source config uses label-based process resources in `conf/base.config`; put custom
  caps in a small server-local config using supported Nextflow `process` selectors or
  `process.resourceLimits`. Do not invent `params.max_cpus`, `params.max_memory`,
  `params.max_time`, or `process.maxCpus`.
- Omit `profile` by default and rely on the server default profile unless the user asks for a
  different runtime or the server default is known to be unsuitable.
- Use `from_run_id` as the public restart path. Read `run_get(detail="full")` on the source run
  when `launch_spec`, `nextflow_session_uuid`, or resume compatibility matters. Do not teach
  raw Nextflow resume fields as public `nextflow_run` inputs.
- After launch, use `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`
  before `run_artifacts`, `run_logs`, or `fs_read`.

## Fast Start

1. Read `assets/playbooks.yaml` and choose the route.
2. Read `references/03_parameters.md` for required placeholders and nextmcp channel boundaries.
3. Use `assets/schema-index.yaml` and one `assets/schema-groups/*.yaml` file when exact type,
   default, enum, or mapping detail matters.
4. Use `assets/artifact-contracts.yaml` and `assets/qc-rules.yaml` after the run reports outputs.
