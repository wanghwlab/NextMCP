# Parameters

Use the presets in `assets/param-presets.yaml` first. Replace every placeholder with a server-local value before launch.

## Required Inputs

- `outdir`: Absolute path on the nextmcp server where results will be saved.
  Placeholder: `<server_output_root>/atacseq`
- `input`: Samplesheet (CSV) with columns sample, fastq_1, fastq_2 (optional), replicate.
  Placeholder: `<server_input_root>/samplesheet.csv`
- `genome` OR (`fasta` + `gtf`): Reference genome. Use `--genome` for AWS iGenomes, or provide FASTA and GTF directly.
- `read_length`: Read length used for MACS2 genome size calculation when `--macs_gsize` is not provided.
  Placeholder: `150`

## Common Route-Shaping Parameters

### Aligner Selection
- `aligner`: Choice of alignment algorithm — `bwa` (default), `bowtie2`, `chromap`, `star`.
- `bwa_index`, `bowtie2_index`, `star_index`, `chromap_index`: Paths to pre-built indices. If omitted, index is built from `--fasta`.
- `save_reference`: Save the generated index to results for reuse.

### Peak Calling
- `narrow_peak`: Run MACS2 in narrowPeak mode instead of default broadPeak.
- `with_control`: Use control samples for peak calling (samplesheet needs control columns).
- `macs_gsize`: Effective genome size for MACS2. Auto-calculated from read_length if omitted.
- `read_length`: Required when macs_gsize is not provided.

### Read Filtering
- `keep_dups`: Do not remove duplicate reads from alignments.
- `keep_mito`: Do not filter mitochondrial reads.
- `keep_multi_map`: Do not filter multi-mapping reads.

### Trimming
- `skip_trimming`: Skip adapter trimming when input is already trimmed.
- `save_trimmed`: Save trimmed FastQ files to results.
- `clip_r1`, `clip_r2`: Remove bp from the 5' end of reads.
- `three_prime_clip_r1`, `three_prime_clip_r2`: Remove bp from the 3' end after adapter trimming.
- `trim_nextseq`: Apply NextSeq-specific quality trimming.
- `min_trimmed_reads`: Minimum trimmed reads threshold; samples below this are removed.

### Intermediate Files
- `save_align_intermeds`: Save library-level and intermediate BAM files.
- `save_unaligned`: Save unaligned reads (STAR and Bowtie2 only).
- `save_macs_pileup`: Save MACS2 bedGraph pileup files.

### QC and Reporting
- `skip_qc`: Skip all QC steps except MultiQC.
- `skip_fastqc`, `skip_picard_metrics`, `skip_preseq`, `skip_plot_fingerprint`, `skip_plot_profile`, `skip_ataqv`, `skip_igv`, `skip_multiqc`: Skip individual QC/reporting steps.
- `skip_peak_qc`, `skip_peak_annotation`: Skip MACS2 QC plots and HOMER annotation.
- `skip_consensus_peaks`: Skip consensus peak generation and featureCounts.
- `skip_deseq2_qc`: Skip DESeq2 PCA and heatmap plotting.
- `skip_merge_replicates`: Skip merged replicate-level analysis.

### Differential Analysis
- `deseq2_vst`: Use vst transformation (default true); set to false for rlog.

### Reference Genome
- `igenomes_ignore`: Do not load iGenomes reference config.
- `blacklist`: Path to blacklist BED file for filtering.
- `gene_bed`: Gene annotation BED file. Generated from GTF if not provided.

## Resource Caps

Put Nextflow config files and resource caps in `nextflow_run(config_files=[...])`.
For this nf-core pipeline, resource caps should use:

```groovy
process {
  resourceLimits = [cpus: 8, memory: '32.GB', time: '24.h']
}
```

Do not invent `params.max_cpus`, `params.max_memory`, `params.max_time`, or
`process.maxCpus`.

## Exact Lookup

- Use `assets/schema-index.yaml` to map a parameter name to its group.
- Open the matching `assets/schema-groups/*.yaml` for exact type, default, enum, and description.
