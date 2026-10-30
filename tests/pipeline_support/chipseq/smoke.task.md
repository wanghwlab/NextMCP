# Task

Use the nextmcp server.
Run the localized `chipseq` lightweight example in project
`pipeline-withskill-chipseq`. Use the rewritten samplesheet and the local genome
FASTA and GTF files. Keep the project-owned default results directory.

## Available inputs

- Input samplesheet: `/data/nextmcp/testdata/chipseq/test/rewrites/pipeline-data/chipseq/samplesheet/v2.1/samplesheet_test_local.csv`
- Reference FASTA: `/data/nextmcp/testdata/chipseq/test/pipeline-data/atacseq/reference/genome.fa`
- Reference GTF: `/data/nextmcp/testdata/chipseq/test/pipeline-data/atacseq/reference/genes.gtf`

## Workflow goal

- Run the upstream lightweight ChIP-seq test route using the local references and localized
  samplesheet.
- Use the default BWA-based alignment route expected by the upstream test.
- Treat the reads as 50 bp reads and keep the speed-oriented fingerprinting behavior used by the
  upstream lightweight test with 100 fingerprinting bins.
- Do not run the library-complexity prediction branch that fails on this small dataset.
- Keep the upstream test resource caps at 2 CPUs, 6.GB memory, and 6.h runtime.

## restrictions
- Do not read pipeline README, docs, schema, source files, or online help.
- Do not inspect `nf_pipeline/chipseq/` materials.
- Do not reference other projects

## Baseline restrictions
- Include all restrictions above.
- Use `baseline-noskill-chipseq` as project name.
- Do not use the `chipseq` expert skill.
