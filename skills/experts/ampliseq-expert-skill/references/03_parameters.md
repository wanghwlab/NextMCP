# Parameters

Use `assets/param-presets.yaml` for common launch shapes. Replace every placeholder with a server-local value confirmed by the user or nextmcp tools.

## Required Choices

`outdir` is required by the schema. A normal run also needs exactly one primary input source:

- `input`: server-local samplesheet, usually preferred.
- `input_folder`: server-local folder of compressed FASTQ files.
- `input_fasta`: server-local ASV or OTU FASTA for taxonomy-focused runs.

Do not mix these input routes unless a source-backed route explicitly requires it, such as `input` plus `multiregion` for Sidle.

## Common Route-Shaping Parameters

- `FW_primer` and `RV_primer`: primer sequences only, without sequencing adapters.
- `metadata`: optional, but needed for many QIIME2 downstream outputs.
- `single_end`, `pacbio`, `iontorrent`, `illumina_novaseq`, `illumina_pe_its`, and `multiple_sequencing_runs`: set only when the data shape requires them.
- `dada_ref_taxonomy`, `sintax_ref_taxonomy`, `kraken2_ref_taxonomy`, `qiime_ref_taxonomy`, `classifier`, and custom database parameters: taxonomy route and prerequisite controls.
- `multiregion`, `sidle_ref_taxonomy`, and Sidle custom reference fields: multi-region route controls.
- `ancom`, `ancombc`, `ancombc_formula`, `picrust`, and `sbdiexport`: downstream output controls.
- `skip_*` and `save_intermediates`: use only when the user asks to remove stages or retain extra files.

## nextmcp Channel Boundaries

Use top-level `project` for the nextmcp project container. Put ordinary ampliseq options in `nextflow_run(params=...)`. Put resource caps and Nextflow config files in `nextflow_run(config_files=[...])`. Use `from_run_id` as the public restart path. Use `extra_args` only when no normalized field covers the needed Nextflow flag.

Resource caps should be provided through a server-local config file, for example:

```nextflow
process { resourceLimits = [cpus: 8, memory: '32.GB', time: '24.h'] }
```

Do not pass `max_cpus`, `max_memory`, or `max_time` inside `params`.

## Exact Lookup

Use `assets/schema-index.yaml` to find the right group. Then open only the matching group under `assets/schema-groups/*.yaml` or `references/schema-groups/*.md` to confirm exact type, default, enum, placeholder, and mapping notes.
