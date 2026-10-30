# Scope And Assumptions

This package supports `nf-core/ampliseq` version 2.16.1 through nextmcp. It was built from a repository-local inspect-equivalent bundle rooted at `/root/key_projects/nextmcp/nf_pipeline/ampliseq`.

## Covered Routes

- FASTQ samplesheet input with `input`.
- FASTQ folder input with `input_folder`.
- Existing ASV or OTU FASTA input with `input_fasta`.
- Illumina paired-end default runs, single-end Illumina, PacBio, IonTorrent, NovaSeq quality handling, and multiple sequencing runs.
- Variable-length ITS handling with `illumina_pe_its` and optional ITSx extraction with `cut_its`.
- Multi-region Sidle analysis with `multiregion` and Sidle taxonomy references.
- DADA2, SINTAX, Kraken2, QIIME2, custom taxonomy databases, trained QIIME2 classifiers, and pplacer.
- Metadata-driven QIIME2 analysis, ADONIS, ANCOM, ANCOM-BC, PICRUSt2, SBDI export, R object outputs, and standard reports.

## Runtime Boundaries

Treat `pipeline="ampliseq"` as the normal pipeline id route. Do not call `nextflow_inspect_pipeline` during ordinary runtime planning or launch.

If a user request depends on an authoring gap, stale coverage claim, or output path uncertainty,
stay inside the packaged runtime assets. Read `assets/authoring-gaps.yaml`, then use
`assets/playbooks.yaml`, `assets/schema-index.yaml`, `assets/schema-groups/*.yaml`,
`assets/artifact-contracts.yaml`, `assets/qc-rules.yaml`, `nextflow_run(prepare=true)`,
`run_get`, and `run_artifacts` as appropriate. If those sources are not enough, state the limit or
scope out the request with a reason, and name `assets/authoring-gaps.yaml` in the answer. Do not
call `nextflow_inspect_pipeline`, inspect the pipeline source, or verify `publishDir` directives as
runtime fallback steps. Source-tree or `publishDir` review belongs to skill maintenance or
regeneration, not to an ordinary runtime answer.

All runtime paths must already exist on the nextmcp server or come from nextmcp outputs. This includes `project`, path-like values in `params`, and any `config_files` entries.

Use `params` for pipeline options. Use `config_files` for Nextflow config files and resource caps. The source config uses `process.resourceLimits`, so a cap config should look like `process { resourceLimits = [cpus: 8, memory: '32.GB', time: '24.h'] }`.
