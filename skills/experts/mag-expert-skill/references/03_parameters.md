# Parameters

Use `assets/param-presets.yaml` for compact route planning. Use `assets/schema-index.yaml` and one
grouped schema file when exact type, default, enum, or a less common parameter matters.

Required everyday values are `input` and `outdir`. Use `assembly_input` only for the pre-computed
assembly route. Use server-scoped placeholders such as `<server_input_root>/samplesheet.csv`,
`<server_input_root>/assemblies.csv`, and `<server_output_root>/mag` while drafting.

The main samplesheet route uses `sample` and `group`, plus read columns and platform columns. For
short reads, confirm `short_reads_1`, optional `short_reads_2`, and `short_reads_platform`. For
long reads, confirm `long_reads` and `long_reads_platform`. Set `single_end` when short reads are
single-end.

Important route-shaping parameters include `assembly_input`, `coassemble_group`,
`binning_map_mode`, `ancient_dna`, `run_virus_identification`, `generate_bigmag_file`, `bbnorm`,
assembler skip flags, binner skip flags, and bin QC or taxonomy switches.

Put ordinary pipeline-facing options in `nextflow_run(params=...)`: input/output paths,
samplesheet mode, assembly and binning selectors, database paths, skip/save toggles, and tool
settings such as `cat_db`, `gtdb_db`, `busco_db`, `checkm_db`, `checkm2_db`, `gunc_db`,
`genomad_db`, `metaeuk_db`, and `host_fasta`.

Put Nextflow config files in `nextflow_run(config_files=[...])`. Resource caps such as max CPUs,
memory, or time must be rendered as a small server-local config file using the pipeline's config
syntax:

```groovy
process {
  resourceLimits = [
    cpus: 16,
    memory: '64.GB',
    time: '24.h',
  ]
}
```

Do not pass `max_cpus`, `max_memory`, or `max_time` through `params`. Do not invent
`process.maxCpus`.

Use `from_run_id` for public restarts. If restart safety matters, read `run_get(detail="full")` on
the source run for `launch_spec`, `nextflow_session_uuid`, `resume_compatible`, and structured compatibility details.
Do not use direct Nextflow resume flags as public `nextflow_run` inputs.

The default route has `run_checkm=false` and `run_checkm2=false`. Do not block a normal run on
`checkm_db` or `checkm2_db`; the default route does not need them unless the user enables CheckM or
CheckM2.

Omit `profile` by default. Rely on `server_info().nextflow.default_profile` unless the user asks for
a different runtime or the server default is unsuitable.
