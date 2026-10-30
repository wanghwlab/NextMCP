# Task

Use the nextmcp server.
Run the localized `rnafusion` reference-build lightweight example in project
`pipeline-withskill-rnafusion`. Use the rewritten FASTQ samplesheet and the
reference/support files listed below. Every path listed below already exists
on the nextmcp server. Keep the project-owned default results directory.

## Available inputs

- Input samplesheet: `/data/nextmcp/testdata/rnafusion/test_build/rewrites/repo-assets/tests/csv/fastq_local.csv`
- FASTQ bundle root: `/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/81cb45949e75cbb85cbf6c5ec9009ab45b160823/testdata/human`
- Minigenome FASTA: `/data/nextmcp/testdata/rnafusion/test_build/downloads/github.com/STAR-Fusion/STAR-Fusion-Tutorial/raw/master/minigenome.fa`
- Minigenome GTF: `/data/nextmcp/testdata/rnafusion/test_build/downloads/github.com/STAR-Fusion/STAR-Fusion-Tutorial/raw/master/minigenome.gtf`
- Arriba protein domains: `/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/refs/heads/rnafusion/testdata/reference/arriba/protein_domains_hg38_GRCh38_v2.5.0.gff3`
- Arriba known fusions: `/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/refs/heads/rnafusion/testdata/reference/arriba/known_fusions_hg38_GRCh38_v2.5.0.tsv.gz`
- Arriba blacklist: `/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/refs/heads/rnafusion/testdata/reference/arriba/blacklist_hg38_GRCh38_v2.5.0.tsv.gz`
- Arriba cytobands: `/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/refs/heads/rnafusion/testdata/reference/arriba/cytobands_hg38_GRCh38_v2.5.0.tsv`
- FusionAnnotator library: `/data/nextmcp/testdata/rnafusion/test_build/downloads/github.com/STAR-Fusion/STAR-Fusion-Tutorial/raw/master/CTAT_HumanFusionLib.mini.dat.gz`
- PFAM HMM: `/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/refs/heads/rnafusion/testdata/human/Pfam-A.hmm.gz`
- DFAM HMM: `/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/refs/heads/rnafusion/testdata/human/test_starfusion_dfam.hmm`
- DFAM H3F: `/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/refs/heads/rnafusion/testdata/human/test_starfusion_dfam.hmm.h3f`
- DFAM H3I: `/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/refs/heads/rnafusion/testdata/human/test_starfusion_dfam.hmm.h3i`
- DFAM H3M: `/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/refs/heads/rnafusion/testdata/human/test_starfusion_dfam.hmm.h3m`
- DFAM H3P: `/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/refs/heads/rnafusion/testdata/human/test_starfusion_dfam.hmm.h3p`
- FusionReport database root: `/data/nextmcp/testdata/rnafusion/test_build/inputs/fusion_report_db`

## Workflow goal

- Run the reference-building route, not a sample-level fusion-calling analysis.
- Build the local support assets for Arriba, STAR-Fusion, FusionReport, Salmon, and FusionInspector.
- Use the rewritten samplesheet so pipeline initialization reads the server-local FASTQ paths already
  recorded in that file.
- Use the listed minigenome FASTA/GTF and support files instead of downloading reference inputs at
  runtime.
- Let the workflow create HGNC reference data during the run rather than binding pre-existing HGNC
  files.
- Use the human GRCh38/gencode v46 minigenome setup with species label `homo_sapiens`, and do not
  require COSMIC inputs.
- Clear any extra arguments for `STARFUSION_BUILD` so that step runs without
  appended build flags.
- Keep the upstream test resource caps at 4 CPUs, 15.GB memory, and 1.h runtime.

## restrictions
- Do not read pipeline README, docs, schema, source files, or online help.
- Do not inspect `nf_pipeline/rnafusion/` materials.
- Do not reference other projects

## Baseline restrictions
- Include all restrictions above.
- Use `baseline-noskill-rnafusion` as project name.
- Do not use the `rnafusion` expert skill.
