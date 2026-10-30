# Troubleshooting

Use summarized runtime reads before raw logs. Start with
`run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`; use `run_logs` or
`fs_read` only after the failing process or log path is known.

If inputs are not found, remember that `input`, `outdir`, references, indices, config files, and
relative path-like params are resolved on the nextmcp server filesystem. Confirm paths with
`fs_list(mode="manifest")`.

If reference setup fails, check whether the run used explicit `fasta` and `gtf`, an iGenomes
reference, or pre-built indices. Pre-built STAR, HISAT2, RSEM, Salmon, and Kallisto indices must
match the genome, annotation, transcriptome, and tool version enough for the selected route.

If STAR fails for memory, either increase resources through `config_files`, use a pre-built
`star_index`, or switch to `aligner: hisat2` if the user accepts no expression quantification from
HISAT2.

If Sentieon STAR fails, check for a missing or invalid `SENTIEON_LICENSE_BASE64` Nextflow secret.
Do not place license material in `params`, docs, or git.

If BAM reprocessing gives odd results, compare the source run's `pipeline_info/params.json` with
the new launch. Keep `skip_alignment: true` and do not mix STAR-Salmon BAMs with STAR-RSEM
reprocessing.

If Salmon-only output is suspect, confirm whether the Salmon index is decoy-aware. If the pipeline
builds a Salmon index without genome FASTA decoys, explain the limitation and prefer a compatible
pre-built `salmon_index` or a rerun with `fasta`.

If UMI output is empty or over-collapsed, re-check where the UMI is stored. Read-name UMIs need
`skip_umi_extract` and a separator. Sequence UMIs need the correct extraction method and barcode
regex.

If contamination results are unexpected, check BBSplit references, SortMeRNA manifest, Kraken2
database host content, and `bracken_precision`. Database choice can dominate interpretation.
