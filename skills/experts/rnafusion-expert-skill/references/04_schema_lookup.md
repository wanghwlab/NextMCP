# Schema Lookup

The package preserves all current `nextflow_schema.json` parameters in grouped schema assets.
Do not scan every group by default. Start with `assets/schema-index.yaml`, then load one group.

## Group Map

- `input_output_options`: samplesheet, tools, reference-building flags, COSMIC route, fusion input
  files, tool-specific reference paths, reporting inputs, and output directory.
- `reference_genome_options`: genome, GENCODE version, read length, and lower-level reference or
  database files.
- `skip_steps`: `skip_qc`, `skip_vis`, and `skip_vcf`.
- `read_trimming_options`: fastp trimming and adapter settings.
- `compression_options`: `cram`.
- `generic_options`: publish mode, notifications, version/help flags, and validation toggles.
- `institutional_config_options`: nf-core institutional config metadata.

## Lookup Steps

1. Find the group in `assets/schema-index.yaml`.
2. Read `references/schema-groups/<group>.md` for a compact list.
3. Read `assets/schema-groups/<group>.yaml` when exact JSON-schema type, default, pattern, enum,
   classification, channel, mapping notes, or `needs_exact_lookup` flags matter.

Every current schema parameter appears in exactly one grouped YAML file.
