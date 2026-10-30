# Task

Use the nextmcp server.
Run the localized `scrnaseq` lightweight example in project
`pipeline-withskill-scrnaseq`. Use the rewritten samplesheet, the local chr19
FASTA and GTF files, and the server-local FASTQ files referenced by the
samplesheet. Keep the project-owned default results directory.

## Available inputs

- Input samplesheet: `/data/nextmcp/testdata/scrnaseq/test/rewrites/pipeline-data/samplesheet-2-0_local.csv`
- Reference FASTA: `/data/nextmcp/testdata/scrnaseq/test/pipeline-data/reference/GRCm38.p6.genome.chr19.fa`
- Reference GTF: `/data/nextmcp/testdata/scrnaseq/test/pipeline-data/reference/gencode.vM19.annotation.chr19.gtf`
- FASTQ bundle root: `/data/nextmcp/testdata/scrnaseq/test/pipeline-data/testdata/cellranger`

## Workflow goal

- Run the localized single-cell RNA-seq lightweight route represented by the rewritten samplesheet.
- Use the STAR-based alignment and counting route for the 10x Genomics v2-style input, using the
  `10XV2` protocol label.
- Do not run the CellBender branch for this small upstream test dataset.
- Use the listed chr19 FASTA and GTF reference files.
- Keep the upstream test resource caps at 2 CPUs, 6.GB memory, and 6.h runtime.

## restrictions
- Do not read pipeline README, docs, schema, source files, or online help.
- Do not inspect `nf_pipeline/scrnaseq/` materials.
- Do not reference other projects

## Baseline restrictions
- Include all restrictions above.
- Use `baseline-noskill-scrnaseq` as project name.
- Do not use the `scrnaseq` expert skill.
