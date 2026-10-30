---
name: sarek-expert-skill
description: Use when the user wants to plan, run, interpret, reuse, or troubleshoot
  nf-core/sarek analyses through nextmcp, including WGS, WES or targeted data,
  germline and somatic variant calling, tumor-normal pairs, UMI handling, BBSplit
  contamination removal, Sentieon routes, CNV or MSI tools, annotation, exact
  parameter lookup, or reruns.
compatibility: Requires access to nextmcp tool docstrings plus server_info, project_list,
  project_get, fs_list, nextflow_run, run_list, run_get, run_artifacts, run_logs,
  fs_read, and nextflow_list_pipelines only when a server-local pipeline root is
  needed for unusual launch checks.
metadata:
  skill-class: expert
  pipeline-id: sarek
  pipeline-version: 3.8.1
  generated-from: authoring bundle rooted at /root/key_projects/nextmcp/nf_pipeline/sarek
---

# nf-core/sarek Expert Skill

## Release and launch selection

This package targets **nf-core/sarek 3.8.1**. For a new remote run, use
`pipeline="nf-core/sarek"` with `extra_args=["-r", "3.8.1"]`. Short pipeline
IDs in historical recipes require a matching configured local catalogue; do not assume
they resolve in a remote-only deployment. For a restart, use `from_run_id` and omit
`project`, `pipeline`, and `run_id`; inspect the stored launch specification first.

## Scope

Expert skill for planning, launching, reviewing, and troubleshooting `nf-core/sarek` through
nextmcp. It covers FastQ, Spring-compressed FastQ, BAM, CRAM, and VCF samplesheets; step-based
starts from mapping, markduplicates, prepare recalibration, recalibrate, variant calling, or
annotation; BWA, BWA-MEM2, DragMap, Parabricks, and Sentieon alignment routes; germline,
tumor-only, and tumor-normal variant calling; CNV, SV, MSI, annotation, UMI, BBSplit, reference
index and cache preparation routes; output review; historical artifact reuse; and schema-backed
exact parameter lookup.

## What This Skill Does Not Handle

- biological interpretation beyond the pipeline's documented output files
- server setup, pipeline installation, container policy, GPU availability, or commercial license
  provisioning
- ordinary runtime planning through authoring-time pipeline inspection; this package already
  contains the source-backed pipeline contract

## Authoritative Assets

- `assets/pipeline-profile.yaml`: scope, modes, assumptions, resource override syntax, and
  server-local path boundary.
- `assets/playbooks.yaml`: user-intent routes and runtime tool order.
- `assets/step-recipes.yaml`: step-level starts, reference/cache preparation, Sentieon, UMI,
  annotation, and restart recipes.
- `assets/param-presets.yaml`: reusable parameter bundles and nextmcp channel boundaries.
- `assets/schema-index.yaml`: map from parameter names and schema groups to exact lookup files.
- `assets/schema-groups/*.yaml`: complete current-schema parameter definitions.
- `assets/artifact-contracts.yaml`: output families, reuse paths, and review order.
- `assets/qc-rules.yaml`: QC signals, failure causes, and next actions.
- `assets/capability-audit.yaml`: source-backed coverage record for high-impact capabilities.
- `assets/authoring-gaps.yaml`: resolved authoring items.

## References

- `references/01_scope_and_assumptions.md`: scope, source basis, and limits.
- `references/02_playbooks.md`: route narratives and workflow choices.
- `references/03_parameters.md`: compact parameter guide and `params` versus `config_files`.
- `references/04_schema_lookup.md`: how to use the grouped schema assets.
- `references/05_outputs_and_qc.md`: output review order and QC interpretation.
- `references/06_troubleshooting.md`: common failure routes and recovery steps.

## Runtime Rules

- Use packaged assets first. Do not start normal runtime planning with authoring-time inspection.
- All runtime `path` values, the `project` identifier, and relative path-like values in `params`
  or `config_files` resolve on the nextmcp server filesystem, not on the client machine.
- Use only server-local paths returned by nextmcp tools or paths the user confirmed already exist
  on the server. Use placeholders such as `<server_input_root>/samplesheet.csv` when drafting.
- Put pipeline-facing options in `nextflow_run(params=...)`: `input`, `outdir`, `step`,
  `genome`, `igenomes_ignore`, reference files, `tools`, `skip_tools`, `aligner`, `wes`,
  `intervals`, UMI settings, save switches, variant-calling switches, annotation settings,
  cache settings, and tool-specific database/index paths.
- Put Nextflow config files and resource caps in `nextflow_run(config_files=[...])`. For this
  pipeline, resource caps should use `process.resourceLimits`; do not invent `params.max_cpus`,
  `params.max_memory`, `params.max_time`, or `process.maxCpus`.
- Omit `profile` by default and rely on the server default profile unless the user asks for a
  different runtime or the server default is known to be unsuitable.
- Use `from_run_id` as the public restart path. Read `run_get(detail="full")` on the source run
  when `launch_spec`, `nextflow_session_uuid`, or resume compatibility matters. Do not teach
  private resume fields as public `nextflow_run` inputs.
- After launch, use `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`
  before `run_artifacts`, `run_logs`, or `fs_read`.

## Fast Start

1. Read `assets/playbooks.yaml` and choose the route.
2. Read `references/03_parameters.md` for required placeholders and nextmcp channel boundaries.
3. Use `assets/schema-index.yaml` and one `assets/schema-groups/*.yaml` file when exact type,
   default, enum, or mapping detail matters.
4. Use `assets/artifact-contracts.yaml` and `assets/qc-rules.yaml` after the run reports outputs.
