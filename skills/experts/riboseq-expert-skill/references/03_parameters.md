# Parameters

Use `assets/param-presets.yaml` for compact route planning. Use `assets/schema-index.yaml` and one
grouped schema file when exact type, default, enum, or a less common parameter matters.

Required everyday values are `input`, `outdir`, and a reference route. For explicit references, use
server-local `fasta` and `gtf`. For iGenomes-style references, use `genome`, but prefer current
explicit references when the user has them.

The samplesheet first five columns are `sample`, `fastq_1`, `fastq_2`, `strandedness`, and `type`.
`strandedness` may be explicit or `auto`. MultiQC reports strand inference and mismatches.

Put ordinary pipeline-facing options in `nextflow_run(params=...)`: input/output paths, reference
paths, `aligner`, `trimmer`, `gencode`, `with_umi`, UMI patterns, `remove_ribo_rna`,
`ribo_database_manifest`, BBSplit settings, `contrasts`, skip toggles, and save toggles.

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


## Requested release

Read `07_version_update.md` for the pinned release's parameter changes, additional routes,
output locations and QC caveats before adapting a previous analysis.
