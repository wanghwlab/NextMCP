# Scope and Assumptions

This package was generated from a repository-local inspect-equivalent bundle built from
`nf_pipeline/mag`. The bundle used the same source categories as a materials inspection payload:
schema, top-level documents, and source files. Targeted source reads covered `docs/usage.md`,
`docs/output.md`, `workflows/mag.nf`, `nextflow.config`, and config examples.

Use this skill for `nf-core/mag` version 5.4.2. The pipeline assembles metagenomic reads, bins
contigs into metagenome-assembled genomes, checks bin quality, classifies taxonomy, annotates
genomes, and can generate ancient DNA, virus, and BIgMAG-specific outputs.

All runtime paths are server-local paths. The `project` argument, `params.input`,
`params.assembly_input`, `params.outdir`, database paths, and relative path-like values in
`config_files` resolve on the nextmcp server filesystem. Do not pass a client-local path unless the
user has confirmed that the same path exists on the server.

The main supported routes are:

- Standard MAG analysis from short reads, long reads, or both.
- Long-read-only assembly with Flye and/or MetaMDBG.
- Hybrid assembly when short and long reads are supplied.
- Pre-computed assembly input with `assembly_input`, which skips read preprocessing and assembly.
- Ancient DNA validation with `ancient_dna`.
- Database-backed bin QC, taxonomy, and annotation.
- Virus identification with geNomad.
- BIgMAG summary generation.
- Historical artifact recovery and rerun planning.

The skill does not stage databases or configure the server runtime. Large database choices must be
confirmed before launch, especially CAT nr, GTDB-Tk, BUSCO, CheckM, CheckM2, GUNC, geNomad, and
MetaEuk.

The default route has `run_checkm=false` and `run_checkm2=false`. Do not block a normal run on
`checkm_db` or `checkm2_db`; the default route does not need them unless the user enables CheckM or
CheckM2.
