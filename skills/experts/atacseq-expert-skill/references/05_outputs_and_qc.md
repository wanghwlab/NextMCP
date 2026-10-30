# Outputs and QC

## Output Review Order

1. **MultiQC report**: `multiqc/<PEAK_TYPE>/multiqc_report.html` — aggregated QC across all samples and tools.
2. **MACS2 peaks**: `<ALIGNER>/merged_library/macs2/<PEAK_TYPE>/` — peak calls, summits, and HOMER annotation.
3. **MACS2 QC**: `<ALIGNER>/merged_library/macs2/<PEAK_TYPE>/qc/` — peak count, FRiP score, and feature ratio plots.
4. **Consensus peaks**: `<ALIGNER>/merged_library/macs2/<PEAK_TYPE>/consensus/` — consensus BED, featureCounts matrix, UpSetR intersections.
5. **DESeq2 QC**: `<ALIGNER>/merged_library/macs2/<PEAK_TYPE>/consensus/deseq2/` — PCA, sample distance heatmap, and normalized counts.
6. **Ataqv metrics**: `<ALIGNER>/merged_library/ataqv/<PEAK_TYPE>/html/` — ATAC-seq specific QC dashboard.
7. **Aligned BAMs**: `<ALIGNER>/merged_library/*.mLb.clN.*.bam` — final filtered, deduplicated alignments.
8. **BigWig tracks**: `<ALIGNER>/merged_library/bigwig/*.bigWig` — normalized coverage tracks for genome browsers.
9. **Picard metrics**: `<ALIGNER>/merged_library/picard_metrics/` — CollectMultipleMetrics and MarkDuplicates outputs.
10. **Preseq complexity**: `<ALIGNER>/merged_library/preseq/*.lc_extrap.txt` — library complexity estimates.
11. **DeepTools coverage**: `<ALIGNER>/merged_library/deeptools/plotfingerprint/` and `plotprofile/` — enrichment QC.
12. **Pipeline info**: `pipeline_info/` — params.json, software versions, and execution reports.

## QC Checks

### Alignment Rate
- Source: `<ALIGNER>/merged_library/samtools_stats/*.flagstat`
- Good: >80% of reads align uniquely to the reference.
- Bad: Alignment rate <50% or excessive unmapped reads.
- Action: Confirm reference genome matches organism. Check trimming efficiency. Verify samplesheet paths.

### Duplication Rate
- Source: `<ALIGNER>/merged_library/picard_metrics/*.metrics.txt`
- Good: Duplication rate within expected ATAC-seq range (<30-50%).
- Bad: Extremely high duplication (>70%) suggesting over-amplification or low input.
- Action: Check if `keep_dups` was enabled. Verify PCR cycle count. Consider increasing sequencing depth.

### Mitochondrial Content
- Source: `<ALIGNER>/merged_library/samtools_stats/*.idxstats`
- Good: Mitochondrial reads are filtered as expected (unless `keep_mito` is set).
- Bad: Mitochondrial reads dominate alignments.
- Action: Verify `keep_mito` is not unintentionally enabled. Review sample quality; high mito content is common in some tissues/cell types.

### Library Complexity
- Source: `<ALIGNER>/merged_library/preseq/*.lc_extrap.txt`
- Good: Preseq curves show good complexity with continued unique read gain.
- Bad: Library complexity is very low (curve plateaus early).
- Action: Review PCR cycles and input DNA amount. Consider deeper sequencing only if complexity supports it.

### Peak Counts and FRiP
- Source: `<ALIGNER>/merged_library/macs2/<PEAK_TYPE>/qc/*.FRiP_mqc.tsv`
- Good: Reasonable peak counts (50k-200k broad, 20k-100k narrow) and FRiP >0.1.
- Bad: Very few peaks or FRiP near zero.
- Action: Check alignment quality and filtering. Verify `narrow_peak` vs `broad_peak` choice. Review read depth.

### Consensus Peak Reproducibility
- Source: `<ALIGNER>/merged_library/macs2/<PEAK_TYPE>/consensus/*.boolean.intersect.plot.pdf`
- Good: UpSetR plots show good overlap across replicates/conditions.
- Bad: Very little consensus peak overlap.
- Action: Verify sample grouping in samplesheet. Check if `min_reps_consensus` should be increased. Review batch effects in DESeq2 PCA.

### DESeq2 Sample Clustering
- Source: `<ALIGNER>/merged_library/macs2/<PEAK_TYPE>/consensus/deseq2/*.plots.pdf`
- Good: PCA and heatmap show samples clustering by biological condition.
- Bad: Samples cluster by technical factors (batch, sequencing lane).
- Action: Review experimental design. Check for batch effects. Consider including batch as a covariate in downstream analysis.

### Ataqv Quality
- Source: `<ALIGNER>/merged_library/ataqv/<PEAK_TYPE>/html/`
- Good: Metrics within expected ATAC-seq ranges.
- Bad: Poor TSS enrichment or abnormal fragment distribution.
- Action: Review TSS enrichment scores and fragment length distributions. Check for nucleosome pattern.

### MultiQC Completeness
- Source: `multiqc/<PEAK_TYPE>/multiqc_report.html`
- Good: Contains FastQC, Trim Galore, samtools, picard, MACS2, and other expected modules.
- Bad: Modules missing or unexpectedly empty.
- Action: If skip flags are enabled, absent modules are expected. Otherwise inspect run logs.

## Historical Reuse

- Search prior runs with `run_list(project=..., artifact_path_contains="multiqc_report.html")`.
- Inspect `run_get(include=["artifact_summary","launch_spec"])`.
- Confirm compatibility via `pipeline_info/params.json`.
- Treat `artifacts.json` and `pipeline_fingerprint` as historical facts.
