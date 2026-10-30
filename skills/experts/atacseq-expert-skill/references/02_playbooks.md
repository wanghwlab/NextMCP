# Playbooks

## standard_atacseq
Standard ATAC-seq analysis with BWA aligner and broad peak calling.
- Confirm server-local input samplesheet and reference genome.
- Default aligner is BWA; default MACS2 mode is broadPeak.
- Use preset `default_atacseq`.

## narrow_peak_calling
Call narrow peaks instead of broad peaks.
- Enable `narrow_peak` for MACS2 narrowPeak mode.
- Can resume from existing broad peak runs without re-running alignment.
- Use preset `narrow_peak`.

## with_controls
Use control/input samples for MACS2 peak calling.
- Samplesheet must include `control` and `control_replicate` columns.
- Control names must match sample column entries.
- Use preset `with_control`.

## alternate_aligner
Switch from default BWA to Bowtie2, Chromap, or STAR.
- Provide pre-built index path to avoid index building time.
- All downstream results are organized under `<ALIGNER>/` directory.
- Use presets `bowtie2_align`, `star_align`, or `chromap_align`.

## skip_trimming_route
Input FastQ files are already adapter-trimmed.
- Use `skip_trimming` only when adapters and low-quality bases are already removed.
- Use preset `skip_trimming_run`.

## save_intermediates
Keep all intermediate files for debugging or benchmarking.
- Enables `save_align_intermeds`, `save_trimmed`, `save_unaligned`, `save_macs_pileup`, `save_reference`.
- Significantly increases disk usage.
- Use preset `save_all_intermediates`.

## deseq2_rlog_transform
Use DESeq2 rlog instead of default vst for smaller experiments.
- Set `deseq2_vst: false`.
- Better suited for small sample sizes where vst may be less stable.
- Use preset `deseq2_rlog`.

## lightweight_run
Skip non-essential QC and reporting to reduce runtime.
- Skips ataqv, plotFingerprint, plotProfile, preseq, and IGV session.
- Core alignment, peak calling, and DESeq2 QC are still performed.
- Use preset `lightweight_run`.

## keep_filtered_reads
Retain duplicate, mitochondrial, or multi-mapped reads.
- Enable `keep_dups`, `keep_mito`, `keep_multi_map`.
- Not recommended for standard ATAC-seq analysis but useful for special cases.
- Use preset `keep_filtered_reads`.

## skip_merge_replicates_route
Do not merge biological replicates.
- Only library-level merging is performed.
- Useful when replicates are biologically distinct.
- Use preset `skip_merge_replicates`.

## resume_or_restart
Recover from a previous run or reuse compatible outputs.
- Search with `run_list(artifact_path_contains="multiqc_report.html")`.
- Inspect `run_get(include=["artifact_summary","launch_spec"])`.
- Confirm compatibility via `pipeline_info/params.json` before reuse.

## troubleshooting_low_signal
Low alignment rate, few peaks, poor FRiP, or high mitochondrial content.
- Review `run_get` diagnosis and `samtools_stats/*.flagstat`.
- Check `picard_metrics/*.metrics.txt` for duplication rate.
- Inspect `macs2/<PEAK_TYPE>/qc/*.FRiP_mqc.tsv` for peak quality.
