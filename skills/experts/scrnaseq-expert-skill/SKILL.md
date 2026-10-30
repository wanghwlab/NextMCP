---
name: scrnaseq-expert-skill
description: Use when the user wants to plan, run, interpret, or troubleshoot nf-core/scrnaseq analyses through nextmcp, including 10x single-cell RNA-seq, STARsolo, Kallisto/BUS, Simpleaf, Cell Ranger, Cell Ranger ARC, Cell Ranger Multi, CellBender filtering, server-local inputs, route-shaping parameters, outputs, or reruns.
compatibility: Requires access to the nextmcp tool docstrings plus server_info, project_list, project_get, fs_list, nextflow_run, run_list, run_get, run_artifacts, run_logs, fs_read, and nextflow_list_pipelines when the runtime needs a server-local pipeline path.
metadata:
  skill-class: expert
  pipeline-id: scrnaseq
  pipeline-version: 4.1.0
  generated-from: authoring bundle rooted at /root/key_projects/nextmcp/nf_pipeline/scrnaseq
---

# nf-core/scrnaseq Expert Skill

## Release and launch selection

This package targets **nf-core/scrnaseq 4.1.0**. For a new remote run, use
`pipeline="nf-core/scrnaseq"` with `extra_args=["-r", "4.1.0"]`. Short pipeline
IDs in historical recipes require a matching configured local catalogue; do not assume
they resolve in a remote-only deployment. For a restart, use `from_run_id` and omit
`project`, `pipeline`, and `run_id`; inspect the stored launch specification first.

## Scope

Expert skill for planning, launching, reviewing, and troubleshooting `nf-core/scrnaseq` runs through nextmcp. Use it for barcode-based single-cell RNA-seq and 10x Genomics routes handled by the pipeline: Simpleaf, STARsolo, Kallisto/BUS, Cell Ranger, Cell Ranger ARC, and Cell Ranger Multi.

## What this skill does not handle

- Smart-seq2 or other plate-based full-length RNA-seq. Route those requests to an RNA-seq pipeline instead.
- Biological interpretation beyond the pipeline's documented matrices, web summaries, QC reports, and trace files.
- Installing licensed tools, building shared server references outside a nextmcp run, or using client-local paths.

## Authoritative Assets

- `assets/pipeline-profile.yaml`: identity, source basis, supported modes, path rules, and resource config syntax. Read first.
- `assets/playbooks.yaml`: route choices for standard Simpleaf, STARsolo, Kallisto/BUS, Cell Ranger, Cell Ranger ARC, Cell Ranger Multi, CellBender, reference reuse, and historical reuse.
- `assets/step-recipes.yaml`: nextmcp tool order and mode-specific launch checks.
- `assets/param-presets.yaml`: compact parameter bundles and placeholders for common routes.
- `assets/schema-index.yaml`: map from parameter names and groups to exact grouped schema files.
- `assets/schema-groups/*.yaml`: complete current schema coverage. Open only the group named by `schema-index.yaml` when exact mapping matters.
- `assets/artifact-contracts.yaml`: output families, handoff files, and artifact fragments for historical search.
- `assets/qc-rules.yaml`: QC signals, likely causes, and follow-up reads.
- `assets/capability-audit.yaml`: source-derived capabilities covered or scoped out by this skill.

## References

- `references/01_scope_and_assumptions.md`: scope, source basis, and non-scope.
- `references/02_playbooks.md`: readable route guide.
- `references/03_parameters.md`: compact parameters and `params` versus `config_files` boundaries.
- `references/04_schema_lookup.md`: how to use the schema index and grouped parameter files.
- `references/05_outputs_and_qc.md`: review order for finished runs.
- `references/06_troubleshooting.md`: common failure routes and restart guidance.

## Runtime Tool Contract

- All runtime `path` values, `project`, and relative path-like values in `params` or `config_files` refer to the nextmcp server filesystem.
- Use only server-local paths returned by nextmcp tools or paths the user already confirmed exist on the server.
- Omit `profile` by default. Rely on `server_info().nextflow.default_profile` unless the user requests another runtime profile or the server default is known to be unsuitable.
- Put ordinary pipeline options under `nextflow_run(params=...)`: `input`, `outdir`, `aligner`, `protocol`, references, indices, samplesheets, and skip/save flags.
- Put Nextflow config files and resource caps in `nextflow_run(config_files=[...])`.
  For this nf-core pipeline, resource caps should use `process { resourceLimits = [...] }`;
  do not invent `params.max_cpus`, `params.max_memory`, `params.max_time`, or
  `process.maxCpus`.
- Use `from_run_id` as the public restart path. For restart planning, inspect the source run with `run_get(detail="full")` first.
- Use `nextflow_run(prepare=true)` before launch when inputs, output layout, restart source, or config files still need checking; inspect `run_layout` and `layout_warnings`.
- After launch, use `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])` before raw logs. Use `run_artifacts(...)` for known sections, `run_logs` for raw Nextflow output, and `fs_read` only for explicit files.
- Do not start normal runtime planning with `nextflow_inspect_pipeline`; this package already contains the pipeline contract.

## Fast Start

1. Read `assets/playbooks.yaml` and choose the route from the requested aligner or assay shape.
2. Read `assets/param-presets.yaml` and replace placeholders with server-local values.
3. If a field needs exact type, enum, or default lookup, open `assets/schema-index.yaml`, then the named `assets/schema-groups/*.yaml` file.
4. For completed runs, start with `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`, then use `assets/artifact-contracts.yaml` and `assets/qc-rules.yaml`.
