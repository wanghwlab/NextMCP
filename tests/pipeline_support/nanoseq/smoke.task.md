# Task

Use the nextmcp server.
Run the localized `nanoseq` lightweight example in project
`pipeline-withskill-nanoseq`. Use the rewritten samplesheet, the local
nondemultiplexed FASTQ, and the server-local reference FASTA copied from the
upstream example. Keep the project-owned default results directory.

## Available inputs

- Input samplesheet: `/data/nextmcp/testdata/nanoseq/test/rewrites/pipeline-data/nanoseq/3.0/samplesheet/samplesheet_nobc_dx_local.csv`
- Nondemultiplexed FASTQ: `/data/nextmcp/testdata/nanoseq/test/pipeline-data/nanoseq/fastq/nondemultiplexed/sample_nobc_dx.fastq.gz`
- Reference FASTA: `/data/nextmcp/testdata/nanoseq/test/pipeline-data/nanoseq/reference/hg19_KCMF1.fa`

## Workflow goal

- Run the DNA Nanopore route represented by the rewritten samplesheet.
- Start from the nondemultiplexed FASTQ and keep the demultiplexing step active with barcode kit
  `NBD103/NBD104`.
- Keep the two sample replicates represented by samplesheet barcodes 6 and 12.
- Align with the default minimap2 path after demultiplexing.
- Skip quantification, genome-browser track generation, fusion analysis, and modification analysis
  branches that are outside this small DNA demultiplexing and alignment test.
- Keep the upstream test resource caps at 2 CPUs, 6.GB memory, and 12.h runtime.

## restrictions
- Do not read pipeline README, docs, schema, source files, or online help.
- Do not inspect `nf_pipeline/nanoseq/` materials.
- Do not reference other projects

## Baseline restrictions
- Include all restrictions above.
- Use `baseline-noskill-nanoseq` as project name.
- Do not use the `nanoseq` expert skill.
