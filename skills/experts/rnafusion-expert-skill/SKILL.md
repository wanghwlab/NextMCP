---
name: rnafusion-expert-skill
description: Use when the user wants to plan, run, interpret, reuse, or troubleshoot
  nf-core/rnafusion fusion-gene detection analyses through nextmcp, especially for
  server-local samplesheets, reference bundles, tool selection, COSMIC/reference
  prerequisites, visualization outputs, QC, CRAM/BAM handling, or reruns.
compatibility: Requires access to the nextmcp tool docstrings plus server_info, project_list,
  project_get, fs_list, nextflow_run, run_list, run_get, run_artifacts, run_logs,
  fs_read, and nextflow_list_pipelines only when a server-local pipeline path is needed.
metadata:
  skill-class: expert
  pipeline-id: rnafusion
  pipeline-version: 4.1.0
  generated-from: authoring bundle rooted at /root/key_projects/nextmcp/nf_pipeline/rnafusion
---

# nf-core/rnafusion Expert Skill

## Release and launch selection

This package targets **nf-core/rnafusion 4.1.0**. For a new remote run, use
`pipeline="nf-core/rnafusion"` with `extra_args=["-r", "4.1.0"]`. Short pipeline
IDs in historical recipes require a matching configured local catalogue; do not assume
they resolve in a remote-only deployment. For a restart, use `from_run_id` and omit
`project`, `pipeline`, and `run_id`; inspect the stored launch specification first.

## Scope

Expert skill for `nf-core/rnafusion` RNA fusion detection through nextmcp. It covers
reference-building, normal fusion detection, selected-tool runs, FusionInspector-only review,
visualization and VCF toggles, QC review, and historical output reuse.

## What this skill does not handle

- clinical interpretation of detected fusions beyond the pipeline output meaning
- building or storing COSMIC credentials for the user
- client-local path upload; nextmcp runtime paths are server-side

## Authoritative Assets

- `assets/pipeline-profile.yaml`: identity, supported modes, assumptions, limits, and source basis. Read first to decide whether the request is in scope.
- `assets/playbooks.yaml`: user-intent routes for reference setup, normal runs, selected tools, FusionInspector-only runs, and result review.
- `assets/step-recipes.yaml`: nextmcp tool order and pipeline step notes for launch, reference building, and post-run review.
- `assets/param-presets.yaml`: reusable schema-backed parameter bundles and placeholders. Read before drafting `nextflow_run` arguments.
- `assets/schema-index.yaml`: map from schema groups to exact grouped parameter files.
- `assets/schema-groups/*.yaml`: complete current-schema parameter definitions. Load only the group named by `schema-index.yaml` when exact mapping is needed.
- `assets/artifact-contracts.yaml`: expected output families, key filenames, and historical reuse hints.
- `assets/qc-rules.yaml`: QC checks, common bad signals, and next actions.
- `assets/capability-audit.yaml`: high-impact capabilities found during authoring and where they are covered.
- `assets/authoring-gaps.yaml`: resolved authoring gaps and any explicit scope-outs.

## References To Read Next

- `references/01_scope_and_assumptions.md`: source basis, runtime assumptions, and path rules.
- `references/02_playbooks.md`: route narratives and decision checks.
- `references/03_parameters.md`: compact parameter guide and `params` versus `config_files` rules.
- `references/04_schema_lookup.md`: how to use the schema index and grouped schema files.
- `references/05_outputs_and_qc.md`: output review order, key files, and QC signals.
- `references/06_troubleshooting.md`: common failure routes and recovery steps.

## Runtime Tool Contract

- Use packaged assets first. Do not start ordinary runtime planning with `nextflow_inspect_pipeline`.
- Optional `server_info()` checks server readiness and the default Nextflow profile when the runtime layout is still unknown.
- Optional `project_list()` discovers the `project` identifier when the user has not named it.
- Optional `project_get(project)` confirms the project root or recent runs before launch or reuse.
- Optional `fs_list(mode="manifest")` checks one concrete server-local input, reference, or output target.
- Use `nextflow_run(prepare=true)` before launch when inputs, output targets, or restart planning still need checking. Read `run_layout` and `layout_warnings` there when project-owned run paths matter.
- Use `nextflow_run` to launch. Put `project`, `run_id`, and `run_name` at the top level. Put pipeline options such as `input`, `outdir`, `tools`, `genomes_base`, `references_only`, `skip_qc`, `skip_vis`, and `skip_vcf` in `params`.
- Put Nextflow config files and resource caps in `nextflow_run(config_files=[...])`.
  For this nf-core pipeline, resource caps should use `process { resourceLimits = [...] }`;
  do not invent `params.max_cpus`, `params.max_memory`, `params.max_time`, or
  `process.maxCpus`.
- Use `from_run_id` as the public restart path. Do not teach hidden resume fields as `nextflow_run` inputs. Inspect `run_get(detail="full")` on the source run when restart compatibility matters.
- After launch, call `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])` before raw logs. Use `run_artifacts(...)` after the summary identifies a relevant artifact section. Use `run_logs` or `fs_read` only for explicit logs or output files.
- For historical reuse, use `run_list(..., artifact_path_contains=...)`, then `run_get(include=["artifact_summary"])`, then `run_artifacts(...)`. Treat `artifacts.json` and `pipeline_fingerprint` as historical facts and confirm route compatibility through `pipeline_info/params_<timestamp>.json` or equivalent run metadata.

## Path Rule

All runtime `path` values, the `project` identifier, and relative path-like values in `params` or
`config_files` are resolved on the nextmcp server filesystem, not on the client machine. Use only
paths returned by nextmcp tools or paths the user already confirmed exist on the server. Prefer
placeholders such as `<server_input_root>/samplesheet.csv`,
`<server_reference_root>/rnafusion`, and `<server_output_root>/rnafusion`.

## Fast Start

1. Read `assets/playbooks.yaml` and choose the route.
2. Read `assets/param-presets.yaml` and `references/03_parameters.md` before drafting `nextflow_run`.
3. Use `assets/schema-index.yaml` plus one grouped schema file when an exact field, default, enum, or pattern matters.
4. Use `assets/artifact-contracts.yaml` and `assets/qc-rules.yaml` after a run finishes or when recovering historical outputs.
