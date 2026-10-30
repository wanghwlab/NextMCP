# Scope And Assumptions

This package was generated from an inspect-equivalent authoring bundle rooted at
`/root/key_projects/nextmcp/nf_pipeline/nanoseq`. The source materials were
`nextflow_schema.json`, `README.md`, top-level docs, `main.nf`, `nextflow.config`, and
`workflows/nanoseq.nf`.

Use this skill for `nf-core/nanoseq` through nextmcp. It covers Nanopore DNA, cDNA, and direct RNA
routes; qcat demultiplexing; NanoLyse filtering; raw-read QC; minimap2 or GraphMap2 alignment;
coverage tracks; DNA variant calling; RNA transcript quantification; differential expression; RNA
modification detection; JAFFAL fusion detection; output review; reruns; and exact schema-backed
parameter lookup.

All runtime paths are server-local paths. The `project` identifier, `params` paths, and
`config_files` paths are resolved on the nextmcp server filesystem. Use only paths returned by
nextmcp tools or paths the user confirmed exist on the server.

The main required fields are `input`, `protocol`, and `outdir`. The input samplesheet has these
columns: `group`, `replicate`, `barcode`, `input_file`, `fasta`, and `gtf`.

The main route limits are source-backed:

- `protocol` must be `DNA`, `cDNA`, or `directRNA`.
- DNA variant calling requires `protocol=DNA` and `call_variants=true`.
- Quantification requires `protocol=cDNA` or `protocol=directRNA`.
- RNA modification analysis requires `protocol=directRNA` and sample directories with `fast5` and
  `fastq` subdirectories.
- JAFFAL fusion analysis runs only for `cDNA` or `directRNA`.
- deepvariant and pepper_margin_deepvariant are documented as Docker/Singularity-only choices.
- `deepvariant_gpu` requires matching server GPU resources.

Do not use authoring-time pipeline inspection for ordinary runtime planning. The package assets are
the runtime source of truth.
