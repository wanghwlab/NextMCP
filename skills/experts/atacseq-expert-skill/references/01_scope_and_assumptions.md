# Scope and Assumptions

Expert skill for `nf-core/atacseq` ATAC-seq peak-calling and differential accessibility analysis built from authoring materials.

## Source Basis

- authoring bundle fields: schema, documents, and source_files
- pipeline directory: /root/key_projects/nextmcp/nf_pipeline/atacseq
- pipeline version: 2.1.2

## What This Skill Covers

- Planning and launching nf-core/atacseq runs on a nextmcp server
- Route selection for different aligners (BWA, Bowtie2, Chromap, STAR)
- Peak calling mode selection (broadPeak vs narrowPeak)
- Control-based peak calling and replicate merging strategies
- Parameter mapping using schema-backed assets
- Output review order and QC interpretation for ATAC-seq specific metrics
- Historical run recovery and safe reuse

## What This Skill Does Not Handle

- Finished downstream interpretation beyond the pipeline's own outputs (e.g. motif analysis, footprinting)
- Infrastructure setup or production guarantees
- Non-ATAC-seq data types (e.g. ChIP-seq, RNA-seq)

## Runtime Boundaries

- Treat `pipeline="atacseq"` as the default pipeline id route.
- Do not call `nextflow_inspect_pipeline` during ordinary runtime planning or launch.
- All runtime paths must already exist on the nextmcp server or come from nextmcp outputs.
- Put Nextflow config files and resource caps in `nextflow_run(config_files=[...])`.
  For this nf-core pipeline, resource caps should use `process { resourceLimits =
  [...] }`; do not invent `params.max_cpus`, `params.max_memory`, `params.max_time`,
  or `process.maxCpus`.
- Use `from_run_id` as the only public restart path.
