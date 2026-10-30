# Scope And Assumptions

Use this skill for `nf-core/chipseq` runs through nextmcp. It covers ChIP-seq
samplesheet checks, reference selection, aligner choice, MACS3 broad or narrow peak
mode, consensus peak quantification, DESeq2 exploratory QC, MultiQC, IGV session
files, output review, historical lookup, and restart planning.

## Source Basis

- authoring bundle fields: schema, documents, and source_files
- pipeline directory: /root/key_projects/nextmcp/nf_pipeline/chipseq
- `README.md`, `docs/usage.md`, `docs/output.md`, `main.nf`, `workflows/chipseq.nf`,
  `nextflow.config`, and `nextflow_schema.json`

## Runtime Boundaries

- Treat `pipeline="chipseq"` as the default pipeline id route.
- Do not call `nextflow_inspect_pipeline` during ordinary runtime planning or launch.
- All runtime paths must already exist on the nextmcp server or come from nextmcp
  outputs.
- Put `project`, `run_id`, `run_name`, and `from_run_id` at the top level of
  `nextflow_run`; put pipeline-facing options in `params`.
- Put Nextflow config files and resource caps in `nextflow_run(config_files=[...])`.
  For this nf-core pipeline, resource caps should use `process { resourceLimits =
  [...] }`; do not invent `params.max_cpus`, `params.max_memory`, `params.max_time`,
  or `process.maxCpus`.
- Omit `profile` unless the user requests a specific runtime or the server default
  is unsuitable.

## Samplesheet Assumptions

The input is a CSV. The first seven columns must be `sample`, `fastq_1`, `fastq_2`,
`replicate`, `antibody`, `control`, and `control_replicate`. Single-end data has an
empty `fastq_2`. FastQ values must point to server-local `.fastq.gz` or `.fq.gz`
files. IP rows with controls should set `antibody`, `control`, and
`control_replicate`; control rows normally leave those three fields blank.

Use identical `sample` and `replicate` values for resequenced runs of the same
library. Biological replicate numbering starts at 1 for each experimental group.
Different antibodies should remain separate because consensus peaks are grouped by
antibody.

## Reference Assumptions

A run can use a configured `genome` key, or explicit server-local reference files.
Without a genome preset, confirm `fasta` plus `gtf` or `gff`. A missing `gene_bed`
can be generated from annotation. Prebuilt indices are preferred for large genomes:
`bwa_index`, `bowtie2_index`, `chromap_index`, or `star_index` depending on
`aligner`. Set `save_reference` only when the pipeline should keep generated indices
under `genome/index/` for future reuse.

The current schema has no separate HOMER database parameter. HOMER annotation in this
pipeline is tied to the supplied GTF/GFF and generated peak files.
