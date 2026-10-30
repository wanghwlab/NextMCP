# Schema Lookup

Use this layer when a specific field needs exact mapping. Do not load every schema group by
default.

1. Read `assets/schema-index.yaml`.
2. Choose the group whose `summary` or `use_when` matches the parameter family.
3. Read the one matching `assets/schema-groups/<group>.yaml` file.
4. Use the record's `name`, `type`, `required`, `default`, `enum`, `description`,
   `classification`, and `mapping_flags` to prepare or validate `nextflow_run(params=...)`.

The current groups are generated from the schema's top-level sections:
`input_output_options`, `reference_genome_options`, `read_trimming_options`,
`read_filtering_options`, `umi_options`, `alignment_options`, `optional_outputs`,
`quality_control`, `process_skipping_options`, `institutional_config_options`, and
`generic_options`.

Use the compact guide in `references/03_parameters.md` for route planning. Use the grouped schema
assets for exact field names, defaults, enum values, or lookup-only fields that are not listed in
the compact guide.
