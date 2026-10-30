# Schema Lookup

The grouped schema layer preserves every current `nextflow_schema.json` parameter exactly once. Use it only when the compact guide is not enough.

## Workflow

1. Open `assets/schema-index.yaml`.
2. Find the group that owns the parameter.
3. Open the matching `assets/schema-groups/<group>.yaml`.
4. Use the grouped record for exact name, type, required status, default, enum values, placeholders, channel, and mapping notes.

## Common Groups

- `input_output_options`: `input`, `outdir`, email, and MultiQC title.
- `mandatory_arguments`: `barcode_whitelist`, `aligner`, and `protocol`.
- `skip_tools`: `skip_multiqc`, `skip_fastqc`, `skip_cellbender`, and deprecated `skip_emptydrops`.
- `reference_genome_options`: `genome`, `fasta`, `gtf`, `transcript_fasta`, `txp2gene`, `save_reference`, and `save_align_intermeds`.
- `simpleaf_options`, `starsolo_options`, `kallisto_bus_options`: aligner-specific controls.
- `cellranger_options`, `cellrangerarc_options`, `cellranger_multi_options`: 10x route controls.
- `generic_options`: nf-core presentation, validation, notification, and hidden helper fields.
