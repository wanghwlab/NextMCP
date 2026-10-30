# Scope And Assumptions

This skill covers `nf-core/scrnaseq` 4.1.0 runtime planning through nextmcp. It was built from a repository-local inspect-equivalent bundle rooted at `nf_pipeline/scrnaseq`, using the current schema, README, top-level docs, `main.nf`, `nextflow.config`, and `workflows/scrnaseq.nf`.

## In Scope

- Barcode-based single-cell RNA-seq routes supported by the pipeline.
- Simpleaf, STARsolo, Kallisto/BUS, Cell Ranger, Cell Ranger ARC, and Cell Ranger Multi route selection.
- Server-local samplesheets, reference paths, prebuilt indices, optional reference building, CellBender filtering, matrix conversion, and output review.
- nextmcp planning, launch shape, restart planning with `from_run_id`, historical artifact recovery, and QC triage.

## Out Of Scope

- Smart-seq2 and other plate-based full-length RNA-seq. Use an RNA-seq workflow instead.
- Installing licensed Cell Ranger software or creating shared references outside a planned nextmcp run.
- Client-local file paths. All paths must be known server-local paths.

## Runtime Boundaries

Use `pipeline="scrnaseq"` for normal launches. Do not call authoring inspection tools during ordinary planning. All runtime `path` values, `project`, and relative path-like values in `params` or `config_files` refer to the nextmcp server filesystem.

Put Nextflow config files and resource caps in `nextflow_run(config_files=[...])`.
For this nf-core pipeline, resource caps should use `process { resourceLimits =
[...] }`; do not invent `params.max_cpus`, `params.max_memory`, `params.max_time`,
or `process.maxCpus`.
