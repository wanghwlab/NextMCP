# Parameters

Use `assets/param-presets.yaml` for launch-ready starting points. Use the grouped schema assets
when exact type, default, enum, or pattern details matter.

## Required Fields

- `tools`: required. Allowed values are `arriba`, `ctatsplicing`, `fusioncatcher`,
  `starfusion`, `stringtie`, `fusionreport`, `fastp`, `salmon`, `fusioninspector`, and `all`.
- `genomes_base`: required. Use a server-local reference root such as
  `<server_reference_root>/rnafusion`.
- `outdir`: required. Use a server-local output path such as `<server_output_root>/rnafusion`.
- `input`: needed for normal analysis. Use a server-local samplesheet path such as
  `<server_input_root>/samplesheet.csv`.

## Route-Shaping Fields

- `references_only`: build references and skip analysis.
- `no_cosmic`: avoid COSMIC when license or credentials are unavailable.
- `cosmic_username`, `cosmic_passwd`, `qiagen`: reference-building credentials and provider route.
- `skip_qc`: skip Picard and other QC-related steps.
- `skip_vis`: skip fusion-report, FusionInspector visualization, and Arriba visualization.
- `skip_vcf`: skip VCF creation.
- `tools_cutoff`: discard fusions detected by fewer than this number of active tools.
- `whitelist`: add custom fusions to FusionInspector input.
- `fusioninspector_fusions`: run FusionInspector with a provided fusion list.
- `arriba_fusions`, `starfusion_fusions`, `fusioncatcher_fusions`: feed prior caller outputs.
- `trim_tail_fusioncatcher`: run extra fastp trimming for FusionCatcher-specific reads.
- `adapter_fasta`, `save_trimmed_fail`, `save_merged`, `min_trimmed_reads`: fastp behavior.
- `cram`: publish CRAM instead of BAM for STAR-aligned output.

## Channel Rules

Put ordinary pipeline options in `params`.

```text
params = {
  "tools": "all",
  "input": "<server_input_root>/samplesheet.csv",
  "genomes_base": "<server_reference_root>/rnafusion",
  "outdir": "<server_output_root>/rnafusion"
}
```

Put Nextflow config files and resource caps in `nextflow_run(config_files=[...])`.
For this nf-core pipeline, resource caps should use:

```groovy
process {
  resourceLimits = [cpus: 8, memory: '32.GB', time: '24.h']
}
```

Do not invent `params.max_cpus`, `params.max_memory`, `params.max_time`, or
`process.maxCpus`. Use process-specific Nextflow syntax only when tuning one process, for example:

```groovy
process {
  withName: 'NFCORE_RNAFUSION:RNAFUSION:BUILD_REFERENCES:FUSIONREPORT_DOWNLOAD' {
    memory = '8.GB'
    cpus = 4
  }
}
```

Use `from_run_id` for public restart. Do not use hidden resume fields as public `nextflow_run`
inputs.

## Exact Lookup

Use `assets/schema-index.yaml` to choose a group, then open only the matching
`assets/schema-groups/<group>.yaml` or `references/schema-groups/<group>.md`.
`input_output_options` contains most rnafusion route fields. `reference_genome_options` contains
reference and database paths. `skip_steps`, `read_trimming_options`, and `compression_options`
cover common mode toggles.
