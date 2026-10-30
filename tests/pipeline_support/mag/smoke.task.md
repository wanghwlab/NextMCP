# Task

Use the nextmcp server.
Run the localized `mag` multirun lightweight example in project
`pipeline-withskill-mag`. Use the rewritten samplesheet, the local BUSCO,
GTDB-Tk, and CAT database bundles, and the server-local paired-end FASTQ files
referenced by the samplesheet. Keep the project-owned default results
directory.

## Available inputs

- Input samplesheet: `/data/nextmcp/testdata/mag/test/rewrites/pipeline-data/mag/samplesheets/samplesheet.multirun.v4_local.csv`
- BUSCO database tarball: `/data/nextmcp/testdata/mag/test/pipeline-data/mag/databases/busco/bacteria_odb10.2024-01-08.tar.gz`
- GTDB-Tk mock database: `/data/nextmcp/testdata/mag/test/pipeline-data/mag/databases/gtdbtk/gtdbtk_mockup_20250422.tar.gz`
- CAT database bundle: `/data/nextmcp/testdata/mag/test/pipeline-data/mag/databases/cat/minigut_cat.tar.gz`
- FASTQ bundle root: `/data/nextmcp/testdata/mag/test/pipeline-data/mag/test_data`

## Workflow goal

- Run the normal paired-end multirun assembly, binning, taxonomy, and annotation route represented
  by the samplesheet.
- Use the listed local BUSCO, GTDB-Tk, and CAT databases instead of downloading databases at
  runtime.
- Keep the lightweight-test behavior that limits unbinned-contig handling to minimum contig length
  1 and at most 2 unbinned contigs.
- Omit the optional ALE, CONCOCT, COMEBin, and MetaBinner steps that the upstream lightweight test
  excludes, while keeping the rest of the multirun MAG route active.
- Keep fast Prokka behavior, BUSCO checking against the `bacteria_odb10` lineage with cleanup, CAT
  output formatting without suggestive asterisks, the MEGAHIT single-CPU fix, and one CPU for
  SPAdes.
- For GTDB-Tk on the tiny mock bins, use full-tree classification, skip the ANI pre-screening step,
  and use a 0.01% completeness threshold.
- Keep the upstream test resource caps at 4 CPUs, 15.GB memory, and 1.h runtime.

## restrictions
- Do not read pipeline README, docs, schema, source files, or online help.
- Do not inspect `nf_pipeline/mag/` materials.
- Do not reference other projects

## Baseline restrictions
- Include all restrictions above.
- Use `baseline-noskill-mag` as project name.
- Do not use the `mag` expert skill.
