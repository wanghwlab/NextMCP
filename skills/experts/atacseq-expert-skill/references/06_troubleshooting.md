# Troubleshooting

## General Diagnostic Order

1. Start with `run_get(include=["progress","diagnosis","next_actions"])`.
2. If the summary is insufficient, use `run_logs()` for Nextflow stdout/stderr.
3. Use `fs_read()` only for one explicit file after you know the path.
4. Use `from_run_id` as the only public restart path when rerun planning matters.

## Common Failures and Recovery

### Low alignment rate
- Check `<ALIGNER>/merged_library/samtools_stats/*.flagstat` for alignment statistics.
- Confirm reference genome matches the organism and samplesheet paths are correct.
- Review `trimgalore/logs/*.log` for adapter trimming efficiency.
- If reads are already trimmed, consider `skip_trimming`.

### Few or no peaks called
- Check `<ALIGNER>/merged_library/macs2/<PEAK_TYPE>/qc/*.FRiP_mqc.tsv` for FRiP scores.
- Verify read depth is sufficient. ATAC-seq typically needs >20M reads per sample for reliable peak calling.
- Confirm `narrow_peak` vs `broad_peak` matches the expected biology.
- Check if `keep_dups` or `keep_mito` unintentionally inflated background signal.

### High mitochondrial content
- Review `<ALIGNER>/merged_library/samtools_stats/*.idxstats` for chromosome mapping distribution.
- Verify `keep_mito` is not enabled unless specifically needed.
- High mitochondrial content is a known ATAC-seq issue for certain cell types/tissues. Consider increasing sequencing depth.

### DESeq2 clustering shows batch effects
- Review `<ALIGNER>/merged_library/macs2/<PEAK_TYPE>/consensus/deseq2/*.plots.pdf`.
- Check samplesheet for batch or lane information.
- Consider explicitly modeling batch in downstream DESeq2 analysis.

### Consensus peak reproducibility is poor
- Review UpSetR plots in `<ALIGNER>/merged_library/macs2/<PEAK_TYPE>/consensus/`.
- Verify replicates are correctly grouped in the samplesheet.
- Check if `min_reps_consensus` should be adjusted.
- Consider whether biological variability explains the low overlap.

### Trimming failures or low retained reads
- Check `trimgalore/logs/*.log` for adapter detection and trimming statistics.
- Default adapter for ATAC-seq is Nextera 'CTGTCTCTTATA'. Verify this matches library prep.
- If input is already trimmed, use `skip_trimming`.
- If samples fail the `min_trimmed_reads` threshold, review input quality.

### Chromap paired-end issues
- Paired-end Chromap output is currently excluded from downstream analysis due to known issues.
- Single-end Chromap data is processed normally.
- Consider Bowtie2 or BWA for paired-end data.

### Resume after failure
- Use `run_get(detail="full")` on the source run to retrieve `launch_spec` and `nextflow_session_uuid`.
- Pass `from_run_id` to `nextflow_run` for the only public restart path.
- Do not use `resume` or a session-id resume parameter as direct `nextflow_run` inputs.
- To add narrow peaks to an existing broad peak run, use `--narrow_peak` with resume without re-running upstream steps.
