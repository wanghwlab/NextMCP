# Parameters

Put ordinary pipeline options in `nextflow_run(params=...)`. Put Nextflow config files and resource
caps in `nextflow_run(config_files=[...])`. Use `from_run_id` for restart. Use `extra_args` only
when no normalized field exists, such as `-entry` for `interactive.nf`.

Required planning fields for most runs are `input` and `outdir`. Standard reference-backed runs
usually need `fasta` and `gtf`, unless the user supplies compatible pre-built indices or a genome
profile that is valid on the server. Keep `igenomes_ignore: true` when using explicit server-local
references.

Route selectors:

- `aligner`: `star_salmon` by default, `star_rsem` for RSEM, `hisat2` for HISAT2 alignment and QC.
- `pseudo_aligner`: `salmon` or `kallisto`; combine with `skip_alignment: true` for
  pseudoalignment-only runs.
- `skip_alignment` and `skip_pseudo_alignment`: use both for preprocessing-only runs.
- `use_sentieon_star`: requires a server-side `SENTIEON_LICENSE_BASE64` Nextflow secret.

Reference and index fields:

- `star_index`, `hisat2_index`, `rsem_index`, `salmon_index`, `kallisto_index` point to compatible
  pre-built indices on the server.
- `save_reference` saves indices built by the pipeline for future reuse.
- `additional_fasta` can add spike-ins, but do not combine it with a user-provided
  `transcript_fasta` unless a compatible pre-built pseudoaligner index already contains those
  sequences.

UMI fields:

- `with_umi` turns on UMI handling.
- `skip_umi_extract` is for UMIs already in read names.
- `umitools_extract_method`, `umitools_bc_pattern`, and `umitools_bc_pattern2` are for
  sequence-embedded UMIs.
- `umi_dedup_tool` selects `umitools` or `umicollapse`.

Filtering and screening fields:

- BBSplit: set `skip_bbsplit: false` and provide `bbsplit_fasta_list` or `bbsplit_index`.
- SortMeRNA: set `remove_ribo_rna: true` and confirm `ribo_database_manifest` or
  `sortmerna_index`.
- Kraken2/Bracken: set `contaminant_screening`, provide `kraken_db`, and choose
  `bracken_precision` when Bracken is used.

Output and QC fields:

- `save_align_intermeds` publishes BAMs and creates `pipeline_info/samplesheet_with_bams.csv` for
  later BAM reprocessing.
- `bam_csi_index` creates CSI indices for large genomes.
- `skip_stringtie`, `skip_bigwig`, `skip_rseqc`, `skip_qualimap`, `skip_biotype_qc`,
  `skip_deseq2_qc`, and `skip_multiqc` remove output families and should be called out to the user.
- `deseq2_vst` controls the DESeq2 QC transform, not differential testing.

For exact defaults, enums, or less common parameters, read `assets/schema-index.yaml` and then the
matching file under `assets/schema-groups/`.
