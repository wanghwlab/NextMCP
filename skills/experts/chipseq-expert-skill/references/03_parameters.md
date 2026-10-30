# Parameters

Use `default_run` first. Replace every placeholder with a server-local value.
All paths are resolved on the nextmcp server filesystem.

## Required Inputs

- `input`: Path to comma-separated file containing information about the samples in the experiment.
  Placeholder: `<server_input_root>/samplesheet.csv`
- `outdir`: The output directory where the results will be saved.
  Placeholder: `<server_output_root>/chipseq`
- `fasta`: Path to FASTA genome file when no configured `genome` key is used.
  Placeholder: `<server_reference_root>/genome.fa`
- `gtf` or `gff`: Annotation path when no configured `genome` key is used.
  Placeholder: `<server_reference_root>/genes.gtf`

## Default Preset

- `input` -> `<server_input_root>/samplesheet.csv`
- `outdir` -> `<server_output_root>/chipseq`
- `fasta` -> `<server_reference_root>/genome.fa`
- `gtf` -> `<server_reference_root>/genes.gtf`
- `aligner` -> `bwa`

## Route-Shaping Parameters

- `aligner`: one of `bwa`, `bowtie2`, `chromap`, or `star`. Use the exact schema
  value. Confirm the matching index path when reusing prebuilt references.
- `narrow_peak`: set true for MACS3 narrowPeak mode. Leave unset for broadPeak mode.
- `read_length`: use when `macs_gsize` is not supplied and the pipeline must derive
  the MACS3 genome size from the reference.
- `save_reference`: keep generated indices under `genome/index/`.
- `keep_dups` and `keep_multi_map`: change filtering behavior. Use only when the
  user asks for that analysis choice.
- `macs_fdr` and `macs_pvalue`: mutually exclusive MACS3 thresholds.
- `min_reps_consensus`: raises the replicate requirement for consensus peaks.
- `deseq2_vst`: controls the DESeq2 transform used in exploratory QC.

## Output And Skip Parameters

Use save flags only when the user needs handoff files: `save_trimmed`,
`save_align_intermeds`, `save_unaligned`, and `save_macs_pileup`. Use skip flags
only when the user accepts missing review signals. Important skip flags include
`skip_qc`, `skip_fastqc`, `skip_trimming`, `skip_preseq`, `skip_spp`,
`skip_plot_profile`, `skip_plot_fingerprint`, `skip_peak_qc`,
`skip_peak_annotation`, `skip_consensus_peaks`, `skip_deseq2_qc`, `skip_igv`, and
`skip_multiqc`.

## nextmcp Boundaries

Keep ordinary pipeline parameters in `nextflow_run(params=...)`: samplesheet,
references, aligner, peak mode, save flags, skip flags, MACS3 thresholds, and report
settings. Keep `project`, `run_id`, `run_name`, and `from_run_id` as top-level
arguments.

Put Nextflow config files and resource caps in `nextflow_run(config_files=[...])`.
For this nf-core pipeline, resource caps should use:

```groovy
process {
  resourceLimits = [cpus: 8, memory: '32.GB', time: '24.h']
}
```

Do not invent `params.max_cpus`, `params.max_memory`, `params.max_time`, or
`process.maxCpus`. Use `from_run_id` for restart planning instead of raw Nextflow
resume flags.

## Exact Lookup

- Use `assets/schema-index.yaml` to choose the right schema group.
- Open the matching grouped reference before the YAML when that is enough.
- Use grouped YAML when exact type, default, enum, pattern, or hidden status matters.
