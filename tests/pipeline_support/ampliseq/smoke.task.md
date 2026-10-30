# Task

Use the nextmcp server.
Run the localized `ampliseq` lightweight example in project
`pipeline-withskill-ampliseq`. Use the rewritten samplesheet, the local metadata
table, and the server-local paired-end FASTQ files referenced by the
samplesheet. Keep the project-owned default results directory.

## Available inputs

- Input samplesheet: `/data/nextmcp/testdata/ampliseq/test/rewrites/pipeline-data/ampliseq/samplesheets/Samplesheet_local.tsv`
- Metadata table: `/data/nextmcp/testdata/ampliseq/test/pipeline-data/ampliseq/samplesheets/Metadata.tsv`
- FASTQ bundle root: `/data/nextmcp/testdata/ampliseq/test/pipeline-data/ampliseq/testdata`
- Local QIIME2 Greengenes85 FASTA: `/data/nextmcp/testdata/ampliseq/test/rewrites/downloads/data.qiime2.org/2023.7/tutorials/training-feature-classifiers/greengenes85.fna`
- Local QIIME2 Greengenes85 taxonomy: `/data/nextmcp/testdata/ampliseq/test/rewrites/downloads/data.qiime2.org/2023.7/tutorials/training-feature-classifiers/greengenes85.tax`

## Workflow goal

- Run the paired-end Illumina amplicon route represented by the samplesheet.
- Use forward primer sequence `GTGYCAGCMGCCGCGGTAA` and reverse primer sequence
  `GGACTACNVGGGTWTCTAAT`.
- Keep the metadata-dependent downstream analyses active, including average barplots, adonis-style
  testing, and ANCOMBC-style differential-abundance testing.
- Use the listed local Greengenes85 reference files instead of downloading taxonomy references at
  runtime.
- Keep DADA2 taxonomic assignment against GTDB release R07-RS207, with the local Greengenes85
  FASTA/taxonomy pair used as the custom QIIME2 reference pair and trimmed to the amplicon region.
- Keep bacterial SSU filtering with the `bac` setting, maximum ASV length 255, at least 2 samples
  per retained feature, and minimum feature frequency 10.
- Use taxonomic agglomeration up to level 4, diversity rarefaction depth 500, VSEARCH clustering,
  and SBDI export behavior used by the upstream lightweight example.
- For metadata-dependent analyses, use average barplot categories `treatment1` and `badpairwise10`,
  adonis-style terms `treatment1` and `mix8`, and ANCOMBC-style testing on `treatment1` with
  reference level `treatment1::b`, effect-size threshold 2, and significance threshold 0.00001.
- Keep the upstream test resource caps at 4 CPUs, 15.GB memory, and 1.h runtime.

## restrictions
- Do not read pipeline README, docs, schema, source files, or online help.
- Do not inspect `nf_pipeline/ampliseq/` materials.
- Do not reference other projects

## Baseline restrictions
- Include all restrictions above.
- Use `baseline-noskill-ampliseq` as project name.
- Do not use the `ampliseq` expert skill.
