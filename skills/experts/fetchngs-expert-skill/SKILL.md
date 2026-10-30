---
name: fetchngs-expert-skill
description: Use when the user wants to plan, run, interpret, reuse, or troubleshoot
  nf-core/fetchngs through nextmcp, especially for accession input files, download
  method choices, metadata-only runs, downstream nf-core samplesheets, dbGaP JWT
  use, server-local outputs, or reruns.
compatibility: Requires access to the nextmcp tool docstrings plus server_info, project_list,
  project_get, fs_list, nextflow_run, run_list, run_get, run_artifacts, run_logs,
  fs_read, and nextflow_list_pipelines when the runtime needs a server-local pipeline
  path for an alternate entry script.
metadata:
  skill-class: expert
  pipeline-id: fetchngs
  pipeline-version: 1.12.0
  generated-from: authoring bundle rooted at /root/key_projects/nextmcp/nf_pipeline/fetchngs
---

# nf-core/fetchngs Expert Skill

## Release and launch selection

This package targets **nf-core/fetchngs 1.12.0**. For a new remote run, use
`pipeline="nf-core/fetchngs"` with `extra_args=["-r", "1.12.0"]`. Short pipeline
IDs in historical recipes require a matching configured local catalogue; do not assume
they resolve in a remote-only deployment. For a restart, use `from_run_id` and omit
`project`, `pipeline`, and `run_id`; inspect the stored launch specification first.

## Scope

Expert skill for `nf-core/fetchngs` public accession metadata, FASTQ download, and samplesheet generation through nextmcp.

## When to use this skill

- the user wants help planning, launching, interpreting, or troubleshooting this pipeline
- the user needs exact parameter lookup from packaged schema assets

## What this skill does not handle

- finished downstream interpretation beyond the pipeline's own outputs
- downstream biological interpretation after FASTQ and samplesheet handoff
- client-local file upload or secret handling outside nextmcp server paths

## Authoritative assets

- `assets/pipeline-profile.yaml`: identity, supported modes, assumptions, and limits. Read first when deciding whether this skill covers the user's request.
- `assets/playbooks.yaml`: user-intent routes and decision rules. Read when choosing a standard, special-mode, or troubleshooting route.
- `assets/step-recipes.yaml`: step-level prerequisites, entry scripts, outputs, and failure checks. Read when planning a partial run or explaining a workflow stage.
- `assets/param-presets.yaml`: reusable launch parameter bundles. Read before drafting `nextflow_run` arguments.
- `assets/schema-index.yaml`: lightweight map from parameter names and groups to the full schema files. Read when an exact parameter name, type, default, or enum matters.
- `assets/schema-groups/*.yaml`: exact grouped parameter definitions from the current schema. Read only the group named by `schema-index.yaml`.
- `assets/capability-audit.yaml`: high-impact capabilities found during authoring and their coverage status. Read while maintaining or reviewing the skill, not for normal runtime planning unless coverage is uncertain.
- `assets/authoring-gaps.yaml`: resolved authoring todos and scoped-out items. Read when reviewing package coverage or maintaining the skill.
- `assets/artifact-contracts.yaml`: expected output families, handoff files, and review order. Read after a run finishes or when planning historical reuse.
- `assets/qc-rules.yaml`: QC checks, thresholds, and interpretation notes. Read when the user asks whether outputs look usable.

## References to read next

- `references/01_scope_and_assumptions.md`: human-readable scope, source basis, and known limits. Read when deciding whether the user request is in scope.
- `references/02_playbooks.md`: route narratives and workflow choices. Read when the asset route needs explanation for a user.
- `references/03_parameters.md`: compact parameter guide, placeholders, and `params` versus `config_files` boundaries. Read before preparing a launch plan.
- `references/04_schema_lookup.md`: how to use `schema-index.yaml` and grouped schema references. Read when a field requires exact schema-backed lookup.
- `references/05_outputs_and_qc.md`: output review order and QC interpretation. Read after `run_get` and `run_artifacts` identify concrete sections or files.
- `references/06_troubleshooting.md`: common failures and recovery routes. Read after summary or logs show a failure mode.

## Operating rules

- Use packaged assets first. Do not start runtime planning with `nextflow_inspect_pipeline`.
- All `path` values, `project`, and relative path-like values in `params` or `config_files` refer to the nextmcp server filesystem.
- Use only paths returned by nextmcp tools or paths the user already confirmed exist on the server.
- The runtime tool subset for this scaffold is: `server_info, project_list, project_get, fs_list, nextflow_run, run_list, run_get, run_artifacts, run_logs, fs_read, nextflow_list_pipelines`.
- Use `run_get(include=[...])` before `run_logs` or `fs_read` after launch.
- Put ordinary fetchngs options such as `input`, `outdir`, `download_method`, `skip_fastq_download`, `nf_core_pipeline`, and `dbgap_key` under `nextflow_run(params=...)`.
- Put Nextflow config files and resource caps in `nextflow_run(config_files=[...])`.
  For this nf-core pipeline, resource caps should use `process { resourceLimits = [...] }`;
  do not invent `params.max_cpus`, `params.max_memory`, `params.max_time`, or
  `process.maxCpus`.
- Use `from_run_id` as the only public restart path. Inspect `run_get(detail="full")` on the source run when restart compatibility matters.
- Omit `profile` by default and rely on the server default profile unless the user asks for a different runtime.

## Fast-start playbooks

1. Read `assets/playbooks.yaml` to choose the route.
2. Read `references/03_parameters.md` for required placeholders and the default preset.
3. Use `references/04_schema_lookup.md` only when exact field mapping matters.
