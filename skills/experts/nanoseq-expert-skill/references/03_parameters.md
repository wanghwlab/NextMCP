# Parameters

Use `assets/param-presets.yaml` for compact route planning. Use `assets/schema-index.yaml` and one
grouped schema file when exact type, default, enum, or a less common parameter matters.

Every launch needs `input`, `protocol`, and `outdir` in `nextflow_run(params=...)`. The samplesheet
columns are `group`, `replicate`, `barcode`, `input_file`, `fasta`, and `gtf`. The `protocol` value
must be `DNA`, `cDNA`, or `directRNA`.

Put ordinary pipeline-facing options in `nextflow_run(params=...)`: demultiplexing fields
(`input_path`, `barcode_kit`, `skip_demultiplexing`, qcat options), alignment fields (`aligner`,
`stranded`, `skip_alignment`), DNA variant fields (`call_variants`, `variant_caller`,
`structural_variant_caller`, `skip_vc`, `skip_sv`), RNA analysis fields
(`quantification_method`, `skip_quantification`, `skip_differential_analysis`,
`skip_modification_analysis`, `skip_xpore`, `skip_m6anet`, `skip_fusion_analysis`,
`jaffal_ref_dir`), and QC skip toggles.

Put Nextflow config files in `nextflow_run(config_files=[...])`. Resource caps such as max CPUs,
memory, or time must be rendered as a small server-local config file using the pipeline's config
syntax:

```groovy
process {
  resourceLimits = [
    memory: 64.GB,
    cpus  : 16,
    time  : 24.h
  ]
}
```

Do not pass `max_cpus`, `max_memory`, or `max_time` through `params`. Do not invent
`process.maxCpus`.

Use `from_run_id` for public restarts. If restart safety matters, read `run_get(detail="full")` on
the source run for `launch_spec`, `nextflow_session_uuid`, and structured compatibility details.
Do not use `resume` as public `nextflow_run` inputs.

Omit `profile` by default. Rely on `server_info().nextflow.default_profile` unless the user asks for
a different runtime or the server default is unsuitable.
