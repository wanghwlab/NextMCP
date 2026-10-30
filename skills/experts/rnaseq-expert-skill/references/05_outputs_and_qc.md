# Outputs and QC

Start with `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`. If the
run completed, inspect `assets/artifact-contracts.yaml` and request the relevant section with
`run_artifacts`.

Review `multiqc/multiqc_report.html` first unless the user asks for a specific file. MultiQC
summarizes FastQC, trimming, SortMeRNA, STAR, RSEM, HISAT2, Salmon, SAMtools, Picard, RSeQC,
Qualimap, Preseq, featureCounts, DESeq2 QC, Kraken2/Bracken, and pipeline metadata when those
steps are enabled.

For STAR-Salmon, check `star_salmon/salmon.merged.gene_counts.tsv`,
`star_salmon/salmon.merged.transcript_counts.tsv`, per-sample `quant.sf`, STAR `Log.final.out`,
SAMtools, Picard, RSeQC, and MultiQC.

For STAR-RSEM, check `star_rsem/rsem.merged.gene_counts.tsv`,
`star_rsem/rsem.merged.transcript_counts.tsv`, per-sample `*.genes.results`, `*.isoforms.results`,
and MultiQC.

For HISAT2, check BAMs and HISAT2 logs. Do not claim expression quantification from this route.

For pseudoalignment-only runs, check `salmon/` or `kallisto/` matrices and per-sample quant files.
For Salmon-only runs, note whether the index was decoy-aware.

For BAM reprocessing, confirm `pipeline_info/samplesheet_with_bams.csv` and compare
`pipeline_info/params.json` against the source run before treating reuse as safe.

QC priorities:

- Low mapping or many unmapped reads: check reference choice, strandedness, contamination,
  trimming, and aligner route.
- Strandedness mismatch: inspect RSeQC infer_experiment and the samplesheet strandedness column.
- Missing quantification: check whether the user selected HISAT2, skipped pseudoalignment, or
  omitted required transcriptome/index inputs.
- UMI problems: check UMI extraction pattern, separator, and deduplication outputs.
- Database-dependent checks: review BBSplit, SortMeRNA, Kraken2, and Bracken database choices and
  license constraints.
- Qualimap feature counts can be misleading in a known edge case; cross-check RSeQC
  `read_distribution.txt`.
