# Troubleshooting

- Start with `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`.
- Use `run_logs()` when the summary is not enough.
- Use `fs_read()` only for one explicit file after you know the path.
- Use `from_run_id` as the only public restart path when rerun planning matters.

## Common Failures

Samplesheet errors usually come from missing first-seven columns, unmatched control
sample names, invalid replicate numbering, missing antibody values for IP rows, or
FastQ paths that are not server-local gzipped FASTQ files. Fix the samplesheet and
rerun prepare before launching.

Reference errors usually come from mixing a `genome` preset with incompatible manual
references, missing `gtf` or `gff` when no genome is used, or reusing an index built
from another FASTA. Confirm paths with `fs_list(mode="manifest")` and verify
`pipeline_info/params.json` for previous reusable outputs.

Alignment failures depend on `aligner`. Confirm that `bwa_index`, `bowtie2_index`,
`chromap_index`, or `star_index` matches the chosen aligner, or provide `fasta` and
decide whether to use `save_reference`. For Bowtie2 or STAR unmapped-read requests,
set `save_unaligned`; it is not a general output for every aligner.

Peak-calling surprises often come from a broad/narrow mode mismatch, missing controls,
incorrect `macs_gsize` or `read_length`, or setting both `macs_fdr` and `macs_pvalue`.
Confirm `narrow_peak`, controls, reference, blacklist, and MACS3 threshold fields
before rerunning.

Missing output sections often come from skip flags. Check `pipeline_info/params.json`
for `skip_multiqc`, `skip_igv`, `skip_consensus_peaks`, `skip_peak_annotation`,
`skip_deseq2_qc`, `skip_spp`, `skip_plot_profile`, and `skip_plot_fingerprint`.

Resource failures should be handled with a server-local config file passed through
`config_files`. For this pipeline, use `process { resourceLimits = [...] }`; do not
invent `params.max_cpus`, `params.max_memory`, `params.max_time`, or
`process.maxCpus`.
