# Scope And Assumptions

This skill was generated from a repository-local inspect-equivalent bundle rooted at
`/root/key_projects/nextmcp/nf_pipeline/rnafusion`. The source material included the current
`nextflow_schema.json`, `README.md`, `docs/usage.md`, `docs/output.md`, `main.nf`,
`nextflow.config`, and `workflows/rnafusion.nf`.

`nf-core/rnafusion` detects and visualizes RNA fusion genes. It can run Arriba, STAR-Fusion,
FusionCatcher, StringTie, CTAT-SPLICING, fusion-report, FusionInspector, Salmon, FastQC, Picard,
and MultiQC. It also has a reference-building route controlled by `references_only`.

## Main Assumptions

- Runtime paths are on the nextmcp server filesystem.
- `tools`, `genomes_base`, and `outdir` are schema-required.
- Normal analysis also needs `input`, a server-local samplesheet.
- The usage docs state that GRCh38 is currently supported.
- The pipeline manifest version in `nextflow.config` is `4.1.0`.
- COSMIC credentials are license-sensitive secrets and must come from the user or the server
  environment.
- Conda and Mamba are not supported when `ctatsplicing` is selected.

## Input Shape

The samplesheet can be CSV, TSV, YAML, or JSON. It must include `sample` and `strandedness`.
Depending on the selected tools, it also needs usable FASTQ, BAM, CRAM, junction, or splice
junction columns. FASTQ is recommended because the workflow can derive missing aligned files from it.

## Reference Shape

`genomes_base` should point to the rnafusion reference root. The docs describe a structure with
tool-specific folders under `<genomes_base>/<genome>/`, including Arriba references,
`fusion_report_db`, GENCODE files, Salmon index, STAR index, STAR-Fusion CTAT genome library, and
HGNC files. If those references are missing, use the reference-building playbook before analysis.

## Runtime Boundaries

Use `params` for pipeline options such as `input`, `outdir`, `tools`, `genomes_base`,
`references_only`, `no_cosmic`, `skip_qc`, `skip_vis`, `skip_vcf`, `tools_cutoff`, `whitelist`,
`fusioninspector_fusions`, `trim_tail_fusioncatcher`, and `cram`.

Put Nextflow config files and resource caps in `nextflow_run(config_files=[...])`.
For this nf-core pipeline, resource caps should use `process { resourceLimits =
[...] }`; do not invent `params.max_cpus`, `params.max_memory`, `params.max_time`,
or `process.maxCpus`. Use process-specific `withName` blocks only for process-level
tuning in addition to the global resource limit.

Use `from_run_id` for public restart planning. Inspect `run_get(detail="full")` on the source run
when `launch_spec`, `nextflow_session_uuid`, or structured restart fields matter.
