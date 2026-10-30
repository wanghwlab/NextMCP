# Parameters

Put ordinary Sarek options in `nextflow_run(params=...)`. Put Nextflow configs and resource caps in
`nextflow_run(config_files=[...])`. Use `from_run_id` for public restarts. Use `extra_args` only
when no normalized nextmcp field covers the needed Nextflow flag.

Every standard run needs `input`, `outdir`, and `step` in params. `step` defaults to `mapping` and
must be one of `mapping`, `markduplicates`, `prepare_recalibration`, `recalibrate`,
`variant_calling`, or `annotate`. Use `assets/schema-index.yaml` and
`assets/schema-groups/input_output_options.yaml` for exact lookup.

The main route selectors are `tools`, `skip_tools`, `aligner`, `wes`, `intervals`, `no_intervals`,
`genome`, `igenomes_ignore`, `build_only_index`, `download_cache`, and `save_reference`. Use
`main_options`, `preprocessing`, `general_reference_genome_options`, and
`reference_genome_options` schema groups for exact values.

Samplesheet rules depend on `step`: mapping uses read inputs, markduplicates and
prepare_recalibration use BAM/CRAM plus indexes, recalibrate also needs recalibration tables,
variant_calling uses BAM/CRAM plus indexes, and annotate uses VCFs.

For resource caps, create a small server-local config and pass it in `config_files`:

```nextflow
process {
  resourceLimits = [cpus: 32, memory: '256.GB', time: '72.h']
}
```

Do not place `max_cpus`, `max_memory`, `max_time`, or `resourceLimits` inside params.
