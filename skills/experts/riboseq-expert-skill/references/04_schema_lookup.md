# Schema Lookup

- Grouping strategy: schema top-level sections from nextflow_schema.json allOf order for riboseq

## Groups

- `input_output_options`: Preserves the original `nextflow_schema.json` top-level section `input_output_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Input/output options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/input_output_options.md`
  Asset: `assets/schema-groups/input_output_options.yaml`
- `reference_genome_options`: Preserves the original `nextflow_schema.json` top-level section `reference_genome_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Reference genome options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/reference_genome_options.md`
  Asset: `assets/schema-groups/reference_genome_options.yaml`
- `read_trimming_options`: Preserves the original `nextflow_schema.json` top-level section `read_trimming_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Read trimming options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/read_trimming_options.md`
  Asset: `assets/schema-groups/read_trimming_options.yaml`
- `read_filtering_options`: Preserves the original `nextflow_schema.json` top-level section `read_filtering_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Read filtering options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/read_filtering_options.md`
  Asset: `assets/schema-groups/read_filtering_options.yaml`
- `umi_options`: Preserves the original `nextflow_schema.json` top-level section `umi_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `UMI options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/umi_options.md`
  Asset: `assets/schema-groups/umi_options.yaml`
- `alignment_options`: Preserves the original `nextflow_schema.json` top-level section `alignment_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Alignment options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/alignment_options.md`
  Asset: `assets/schema-groups/alignment_options.yaml`
- `riboseq_specific_options`: Preserves the original `nextflow_schema.json` top-level section `riboseq_specific_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Riboseq-specific options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/riboseq_specific_options.md`
  Asset: `assets/schema-groups/riboseq_specific_options.yaml`
- `optional_outputs`: Preserves the original `nextflow_schema.json` top-level section `optional_outputs` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Optional outputs` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/optional_outputs.md`
  Asset: `assets/schema-groups/optional_outputs.yaml`
- `process_skipping_options`: Preserves the original `nextflow_schema.json` top-level section `process_skipping_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Process skipping options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/process_skipping_options.md`
  Asset: `assets/schema-groups/process_skipping_options.yaml`
- `institutional_config_options`: Preserves the original `nextflow_schema.json` top-level section `institutional_config_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Institutional config options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/institutional_config_options.md`
  Asset: `assets/schema-groups/institutional_config_options.yaml`
- `generic_options`: Preserves the original `nextflow_schema.json` top-level section `generic_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Generic options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/generic_options.md`
  Asset: `assets/schema-groups/generic_options.yaml`