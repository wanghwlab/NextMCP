# Parameters

Use `assets/param-presets.yaml` for route presets and `assets/schema-index.yaml` for exact lookup. Replace every placeholder with a server-local value.

## Required Inputs

- `input`: server-local CSV samplesheet. Placeholder: `<server_input_root>/samplesheet.csv`.
- `outdir`: server-local results directory. Placeholder: `<server_output_root>/methylseq`.
- `aligner`: required enum. Valid values are `bismark`, `bismark_hisat`, `bwameth`, and `bwamem`.

Reference requirements depend on the route:

- Bismark or Bismark-HISAT2: use configured `genome`, or provide `fasta` plus `bismark_index`.
- BWA-Meth: use configured `genome`, or provide `fasta`, `fasta_index`, and `bwameth_index`.
- BWA-MEM/TAPS: use configured `genome`, or provide `fasta`, `fasta_index`, and `bwamem_index`.

The source docs state that explicit prebuilt index use still requires `fasta`.

## Route-Shaping Parameters

- `aligner`: chooses Bismark, Bismark-HISAT2, BWA-Meth, or BWA-MEM.
- `use_mem2`: applies only to `aligner=bwameth`.
- `taps`: TAPS route; prefer `aligner=bwamem`.
- `run_targeted_sequencing`, `target_regions_file`, `collecthsmetrics`: target-region analysis and optional Picard metrics.
- `pbat`, `rrbs`, `single_cell`, `accel`, `zymo`, `em_seq`, `nomeseq`, `slamseq`: special library or assay flags.
- `non_directional`, `cytosine_report`, `comprehensive`, `all_contexts`, `merge_context`, `methyl_kit`: methylation calling or output shape.
- `run_qualimap`, `run_preseq`, `save_align_intermeds`, `save_trimmed`, `unmapped`, `save_reference`: optional outputs and QC.
- `skip_trimming`, `skip_trimming_presets`, `skip_deduplication`, `skip_fastqc`, `skip_multiqc`: step skipping. Use with care because they affect QC and artifact contracts.

## Channel Boundaries

Put ordinary pipeline options under `nextflow_run(params=...)`: `input`, `outdir`, `aligner`, `genome`, `fasta`, index paths, `taps`, `run_targeted_sequencing`, and optional QC switches.

Keep `project`, `pipeline`, optional `run_id`, optional `run_name`, and `from_run_id` as top-level `nextflow_run` fields. `from_run_id` is the public restart path.

Put Nextflow config files and small server-local resource override configs in `config_files`. Resource caps such as `max_cpus`, `max_memory`, and `max_time` are not methylseq params. Use Nextflow config syntax accepted by the server, such as process selectors or `process.resourceLimits`, and pass that server-local config through `config_files`.

Use `extra_args` only when no normalized field covers the required Nextflow flag.

Omit `profile` by default. Use it only when the user requests a different runtime, such as GPU, or when the server default is unsuitable.

## Exact Lookup

When a parameter name, type, enum, default, or mapping is uncertain:

1. Open `assets/schema-index.yaml`.
2. Find the parameter group.
3. Open only the matching `assets/schema-groups/<group>.yaml` or `references/schema-groups/<group>.md`.

Every current schema parameter appears in exactly one grouped schema asset.
