# Task

Use the nextmcp server.
Run the prepared mixed RNA-seq and Ribo-seq lightweight example in project
`pipeline-withskill-riboseq`. Use the localized chr20 references, the localized
contrasts table, and the localized SortMeRNA database manifest. Keep the
project-owned default results directory.

## Available inputs

- Samplesheet: `/data/nextmcp/testdata/riboseq/test/rewrites/pipeline-data/riboseq/samplesheet/samplesheet_local.csv`
- Contrasts table: `/data/nextmcp/testdata/riboseq/test/pipeline-data/riboseq/contrasts.csv`
- Genome FASTA: `/data/nextmcp/testdata/riboseq/test/pipeline-data/modules/data/genomics/homo_sapiens/riboseq_expression/Homo_sapiens.GRCh38.dna.chromosome.20.fa.gz`
- Annotation GTF: `/data/nextmcp/testdata/riboseq/test/pipeline-data/modules/data/genomics/homo_sapiens/riboseq_expression/Homo_sapiens.GRCh38.111_chr20.gtf`
- rRNA database manifest: `/data/nextmcp/testdata/riboseq/test/rewrites/pipeline-data/riboseq/testdata/rrna-db_local.txt`

## Workflow goal

- Run the mixed RNA-seq and Ribo-seq test design represented by the samplesheet.
- Use the contrasts table so translational-efficiency outputs remain part of the run.
- Use the localized chr20 genome, annotation, and SortMeRNA database manifest.
- Keep STAR alignment, Salmon quantification, Ribo-TISH quality-control outputs, and
  translational-efficiency outputs active.
- Keep the trimmed-read minimum at 1000 for this lightweight test.
- Do not run the Ribotricer branch for this lightweight test.
- Keep the upstream test resource caps at 4 CPUs, 15.GB memory, and 1.h runtime.

## restrictions
- Do not read pipeline README, docs, schema, source files, or online help.
- Do not inspect `nf_pipeline/riboseq/` materials.
- Do not reference other projects

## Baseline restrictions
- Include all restrictions above.
- Use `baseline-noskill-riboseq` as project name.
- Do not use the `riboseq` expert skill.
