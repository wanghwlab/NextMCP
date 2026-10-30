---
name: riboseq-expert-skill
description: Use when the user wants to plan, run, interpret, or troubleshoot nf-core/riboseq analyses
  through nextmcp, including Ribo-seq, TI-seq, UMI-aware runs, Bowtie2 rRNA and tRNA depletion, BBSplit screening,
  ORF prediction, Salmon quantification, translational efficiency, exact parameter lookup, or reruns.
metadata:
  skill-class: expert
  pipeline-id: riboseq
  pipeline-version: 2.0.0
  generated-from: https://github.com/nf-core/riboseq/tree/2.0.0
compatibility: Requires nextmcp runtime tools and server-confirmed inputs. Uses the official remote
  workflow with an explicit release; no custom local entry scripts are assumed.
---

# nf-core/riboseq Expert Skill

## Scope

Expert skill for planning, launching, reviewing, and troubleshooting `nf-core/riboseq` through
nextmcp. It covers the main Ribo-seq workflow, optional UMI handling, rRNA filtering, BBSplit
contaminant screening, Ribo-TISH and Ribotricer outputs, Salmon quantification, matched
RNA-seq/Ribo-seq translational efficiency analysis, and version-specific ORF and quantification modes.

## What this skill does not handle

- biological interpretation beyond the pipeline's documented outputs
- server setup, pipeline installation, or container/runtime policy decisions
- ordinary runtime planning through `nextflow_inspect_pipeline`; pipeline material inspection
  is an optional authoring step, not a routine execution prerequisite

## Authoritative Assets

- `assets/playbooks.yaml`: route selection and prerequisites.
- `assets/param-presets.yaml`: parameter fragments and channel boundaries.
- `assets/schema-index.yaml`: index of grouped parameter definitions.
- `assets/artifact-contracts.yaml`: outputs and conditions for producing them.
- `assets/qc-rules.yaml`: quality checks and corrective actions.
- `assets/authoring-gaps.yaml`: documented knowledge gaps.
- `assets/source-provenance.yaml`: versioned sources and checksums.

## References

- `references/01_scope_and_assumptions.md`: scope, source basis, and limits.
- `references/02_playbooks.md`: route narratives and workflow choices.
- `references/03_parameters.md`: compact parameter guide and `params` versus `config_files`.
- `references/04_schema_lookup.md`: how to use the grouped schema assets.
- `references/05_outputs_and_qc.md`: output review order and QC interpretation.
- `references/06_troubleshooting.md`: common failure routes and recovery steps.

## Runtime Rules

- For the requested combined rRNA + tRNA depletion route, explicitly use
  `remove_ribo_rna=true` and `ribo_removal_tool="bowtie2"`. Supply a confirmed
  `ribo_database_manifest` with reference FASTAs covering both RNA classes, one path per line.
  The default rRNA references do not establish tRNA coverage. SortMeRNA remains the upstream
  default; Bowtie2 is the selected route for this combined-depletion requirement.
- Use packaged assets first. Do not start normal runtime planning with `nextflow_inspect_pipeline`.
- All runtime `path` values, the `project` identifier, and relative path-like values in `params`
  or `config_files` resolve on the nextmcp server filesystem, not on the client machine.
- Use only paths returned by nextmcp tools or paths the user confirmed already exist on the
  server. Use placeholders such as `<server_input_root>/samplesheet.csv` when drafting.
- Put pipeline-facing options in `nextflow_run(params=...)`: input, outdir, references, route
  selectors, UMI settings, rRNA/BBSplit settings, and skip/save toggles.
- Put Nextflow config files and resource caps in `nextflow_run(config_files=[...])`. For this
  pipeline, resource caps should use `process { resourceLimits = [...] }`; do not invent
  `params.max_cpus`, `params.max_memory`, `params.max_time`, or `process.maxCpus`.
- Omit `profile` by default and rely on the server default profile unless the user asks for a
  different runtime or the server default is known to be unsuitable.
- Use `from_run_id` as the public restart path. Read `run_get(detail="full")` on the source run
  when `launch_spec`, `nextflow_session_uuid`, or resume compatibility matters. Do not teach
  `resume` as public `nextflow_run` inputs.
- After launch, use `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`
  before `run_artifacts`, `run_logs`, or `fs_read`.

## Fast Start

1. Read `assets/playbooks.yaml` and choose the route.
2. Read `references/03_parameters.md` for required placeholders and nextmcp channel boundaries.
3. Use `assets/schema-index.yaml` and one `assets/schema-groups/*.yaml` file when exact type,
   default, enum, or mapping detail matters.
4. Use `assets/artifact-contracts.yaml` and `assets/qc-rules.yaml` after the run reports outputs.

## Versioned official source

This package targets **nf-core/riboseq 2.0.0**. Read `references/07_version_update.md`
for release-specific changes and `assets/source-provenance.yaml` for source checksums.
For a new run, use `pipeline="nf-core/riboseq"` with `extra_args=["-r", "2.0.0"]`.
Do not silently substitute a local short ID or another release. Use server-confirmed input paths.
A remote target does not support nextmcp's local-only `validate_params_schema=true`;
the pipeline still performs its own validation. Resume uses `from_run_id` after inspecting
the stored launch specification. With `from_run_id`, omit `project`, `pipeline`, and `run_id`; the server recovers them from the source run. Do not add a new release pin to a resume request.
