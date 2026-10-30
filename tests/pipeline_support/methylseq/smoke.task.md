# Task

Use the nextmcp server.
Run the localized `methylseq` lightweight example in project
`pipeline-withskill-methylseq`. Use the rewritten samplesheet, the local genome
FASTA and FASTA index, and the server-local FASTQ files referenced by the
samplesheet. Keep the project-owned default results directory.

## Available inputs

- Input samplesheet: `/data/nextmcp/testdata/methylseq/test/rewrites/repo-assets/assets/samplesheet_local.csv`
- Genome FASTA: `/data/nextmcp/testdata/methylseq/test/pipeline-data/methylseq/reference/genome.fa.gz`
- Genome FASTA index: `/data/nextmcp/testdata/methylseq/test/pipeline-data/methylseq/reference/genome.fa.fai`
- FASTQ bundle root: `/data/nextmcp/testdata/methylseq/test/pipeline-data/methylseq/testdata`

## Workflow goal

- Run the upstream lightweight methylation-analysis route represented by the rewritten samplesheet.
- Keep the provided mix of single-end reads and paired-end methylated control reads.
- Use the listed local genome FASTA and FASTA index instead of genome lookup or igenomes lookup.
- Keep the default Bismark alignment, deduplication, methylation extraction, FastQC, and MultiQC
  behavior.
- Keep the upstream test resource caps at 4 CPUs, 15.GB memory, and 1.h runtime.

## restrictions
- Do not read pipeline README, docs, schema, source files, or online help.
- Do not inspect `nf_pipeline/methylseq/` materials.
- Do not reference other projects

## Baseline restrictions
- Include all restrictions above.
- Use `baseline-noskill-methylseq` as project name.
- Do not use the `methylseq` expert skill.
