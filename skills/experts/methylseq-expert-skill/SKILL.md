---
name: methylseq-expert-skill
description: Use whenever the user wants to plan, run, interpret, reuse, or troubleshoot nf-core/methylseq through nextmcp, including Bismark, Bismark-HISAT2, BWA-Meth, BWA-MEM/TAPS, targeted methylation, special library presets, server-local references, outputs, QC, or reruns.
compatibility: Requires access to the nextmcp tool docstrings plus server_info, project_list, project_get, fs_list, nextflow_run, run_list, run_get, run_artifacts, run_logs, and fs_read.
metadata:
  skill-class: expert
  pipeline-id: methylseq
  pipeline-version: 4.2.0
  generated-from: repository-local inspect-equivalent bundle rooted at /root/key_projects/nextmcp/nf_pipeline/methylseq
---

# nf-core/methylseq Expert Skill

## Release and launch selection

This package targets **nf-core/methylseq 4.2.0**. For a new remote run, use
`pipeline="nf-core/methylseq"` with `extra_args=["-r", "4.2.0"]`. Short pipeline
IDs in historical recipes require a matching configured local catalogue; do not assume
they resolve in a remote-only deployment. For a restart, use `from_run_id` and omit
`project`, `pipeline`, and `run_id`; inspect the stored launch specification first.

## Scope

Use this skill for nf-core/methylseq runs through nextmcp. It covers Bismark, Bismark-HISAT2, BWA-Meth, BWA-MEM/TAPS with Rastair, targeted sequencing, library presets, optional QC outputs, historical output lookup, and source-backed parameter lookup.

## Non-Scope

- Do not use this skill for long-read methylation pipelines.
- Do not use it to install server runtimes, containers, GPU drivers, or reference databases.
- Do not start normal runtime planning with `nextflow_inspect_pipeline`; authoring already packaged the current contract.

## Authoritative Assets

- `assets/pipeline-profile.yaml`: pipeline identity, required inputs, supported routes, assumptions, and limits.
- `assets/playbooks.yaml`: user-intent routes for Bismark, BWA-Meth, TAPS, targeted sequencing, optional QC, and reuse.
- `assets/step-recipes.yaml`: launch order, reference preflight, route steps, targeted sequencing, and restart rules.
- `assets/param-presets.yaml`: reusable parameter bundles and server-local placeholders.
- `assets/schema-index.yaml`: map from exact parameter names to grouped schema files.
- `assets/schema-groups/*.yaml`: complete current-schema parameter records.
- `assets/artifact-contracts.yaml`: published output families, review order, and reuse search fragments.
- `assets/qc-rules.yaml`: QC checks, bad signals, and next actions.
- `assets/capability-audit.yaml`: source-derived capability coverage for maintenance review.
- `assets/authoring-gaps.yaml`: resolved or scoped-out authoring items.

## References

- `references/01_scope_and_assumptions.md`: scope, source basis, and route summary.
- `references/02_playbooks.md`: route narratives and nextmcp call order.
- `references/03_parameters.md`: compact parameter guide and channel boundaries.
- `references/04_schema_lookup.md`: how to use `schema-index.yaml` and grouped schema references.
- `references/05_outputs_and_qc.md`: output review order and QC interpretation.
- `references/06_troubleshooting.md`: common failures and recovery routes.

## Runtime Tool Contract

Use packaged assets first. Optional discovery calls are only for missing runtime context:

- `server_info()` when the runtime layout or default profile is unknown.
- `project_list()` when the project id is unknown.
- `project_get(project)` when the project root or recent runs matter.
- `fs_list(mode="manifest")` for one concrete server-local path that needs confirmation.
- `nextflow_run(prepare=true)` before launch when inputs, output target, restart, or run layout still needs checking.
- `nextflow_run` to launch with `project` as a top-level argument and ordinary pipeline options in `params`.
- `run_list(project=..., pipeline="methylseq", artifact_path_contains=...)` when recovering a prior run from a remembered artifact fragment.
- `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])` before raw logs or file reads.
- `run_get(detail="full")` when concrete project-owned layout paths, `launch_spec`, `nextflow_session_uuid`, or restart compatibility matter.
- `run_artifacts(...)` after the summary identifies relevant artifact sections.
- `run_logs` only when the summary is not enough.
- `fs_read` only for explicit logs, reports, params files, or output files after their server-local paths are known.

`nextflow_run` boundaries: `project`, optional `run_id` / `run_name`, `pipeline`, and `from_run_id` are top-level run fields. Put pipeline parameters such as `input`, `outdir`, `aligner`, `fasta`, `bismark_index`, `taps`, and `run_targeted_sequencing` under `params`. Use `config_files` for Nextflow config files and small server-local override configs. Use `from_run_id` as the public restart path. Use `extra_args` only when no normalized field covers a needed Nextflow flag.

Resource caps such as `max_cpus`, `max_memory`, and `max_time` belong in a small server-local override config passed through `config_files`, not in `params`. The methylseq source does not define a pipeline-specific resource-cap parameter; keep overrides in Nextflow config syntax such as process selectors or `process.resourceLimits` when that is the server's supported pattern.

Omit `profile` by default and rely on `server_info().nextflow.default_profile` when runtime environment choice matters. Pass `profile` explicitly only when the user requests a different runtime, such as GPU for BWA-Meth, or the server default is unsuitable.

## Path Boundary

All runtime `path` values, the `project` identifier, and relative path-like values in `params` or `config_files` are resolved on the nextmcp server filesystem, not on the client machine. Use only paths returned by nextmcp tools or paths the user already confirmed exist on the server. Use placeholders such as `<server_input_root>/samplesheet.csv`, `<server_reference_root>/genome.fa`, and `<server_output_root>/methylseq`.

## Fast Start

1. Read `assets/playbooks.yaml` and choose the route: Bismark, Bismark-HISAT2, BWA-Meth, BWA-MEM/TAPS, targeted sequencing, optional QC, or historical reuse.
2. Read `references/03_parameters.md` and `assets/param-presets.yaml` before drafting `nextflow_run` arguments.
3. Use `assets/schema-index.yaml` and one `assets/schema-groups/*.yaml` file when exact type, enum, default, or mapping is needed.
4. After launch, start with `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`, then use `run_artifacts(...)`, then read explicit files.
