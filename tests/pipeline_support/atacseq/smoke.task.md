# Task

Use the nextmcp server.
Run the localized `atacseq` lightweight example in project
`pipeline-withskill-atacseq`. Use the rewritten samplesheet, the local genome
FASTA and GTF files, and the local FASTQ files referenced by the samplesheet.
Keep the project-owned default results directory.

## Available inputs

- Input samplesheet: `/data/nextmcp/testdata/atacseq/test/rewrites/pipeline-data/samplesheet/v2.0/samplesheet_test_local.csv`
- Reference FASTA: `/data/nextmcp/testdata/atacseq/test/pipeline-data/reference/genome.fa`
- Reference GTF: `/data/nextmcp/testdata/atacseq/test/pipeline-data/reference/genes.gtf`
- Localized dataset root: `/data/nextmcp/testdata/atacseq/test/pipeline-data`

## Workflow goal

- Run the upstream lightweight ATAC-seq test route using the local genome files and localized FASTQ
  paths.
- Use the default BWA-based alignment path expected by the upstream test.
- Treat the test reads as 50 bp reads and keep `MT` as the mitochondrial chromosome name used by
  the local reference bundle.
- Keep the speed-oriented fingerprinting behavior from the upstream lightweight test by using
  100 fingerprinting bins.
- Keep the upstream test resource caps at 2 CPUs, 6.GB memory, and 6.h runtime.

## restrictions
- Do not read pipeline README, docs, schema, source files, or online help.
- Do not inspect `nf_pipeline/atacseq/` materials.
- Do not reference other projects

## Baseline restrictions
- Include all restrictions above.
- Use `baseline-noskill-atacseq` as project name.
- Do not use the `atacseq` expert skill.
