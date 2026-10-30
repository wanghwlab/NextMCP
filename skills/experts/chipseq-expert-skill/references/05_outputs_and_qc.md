# Outputs And QC

Start with `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`.
Then use `run_artifacts(...)` to locate concrete output sections. Use `fs_read` only
after a specific report, table, or log path is known.

## Review Order

1. `pipeline_info/params.json` to confirm the launch route, aligner, peak mode, skip
   flags, and saved-output flags.
2. `multiqc/<PEAK_TYPE>/multiqc_report.html` as the main aggregate QC entry point.
3. `<ALIGNER>/merged_library/` for filtered BAMs, samtools statistics, Picard metrics,
   and Preseq output.
4. `<ALIGNER>/merged_library/phantompeakqualtools/` and deepTools outputs for ChIP
   enrichment QC.
5. `<ALIGNER>/merged_library/macs3/<PEAK_TYPE>/` for MACS3 peaks, HOMER annotation,
   FRiP, peak counts, and peak QC plots.
6. `<ALIGNER>/merged_library/macs3/<PEAK_TYPE>/consensus/<ANTIBODY>/` for consensus
   peaks, featureCounts matrices, boolean peak tables, and DESeq2 QC.
7. `igv/<PEAK_TYPE>/igv_session.xml` for genome browser review.

## QC Signals

For SPP, NSC above 1.05 and RSC above 0.8 are useful ENCODE-style signals for
acceptable ChIP enrichment. Low values can reflect weak ChIP, low signal-to-noise,
shallow sequencing, poor sequence quality, mis-mapping, or a mark with few true
binding sites. Compare these with FastQC, alignment, duplication, and peak-count
sections before drawing conclusions.

For peaks, review peak count, FRiP score, fold-change distribution, HOMER annotation,
and whether the selected peak mode matches the assay. `narrowPeak` is usually for
narrow marks such as transcription factors; broadPeak is the default and often fits
broad histone marks.

For consensus outputs, review per-antibody consensus peak sets, featureCounts read
assignment, replicate overlap, PCA, and sample-distance heatmaps. Raising
`min_reps_consensus` creates a stricter consensus set and can remove replicate-unique
peaks.

## Historical Reuse

Use `run_list(project=..., pipeline="chipseq", artifact_path_contains=...)` when the
user remembers a filename or output fragment. Use `run_get(include=["artifact_summary"])`
and `run_artifacts(...)` before reading files. Treat `artifacts.json` and
`pipeline_fingerprint` as historical facts, then confirm compatibility through
`pipeline_info/params.json`.
