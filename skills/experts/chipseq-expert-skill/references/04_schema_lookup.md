# Schema Lookup

- Grouping strategy: schema top-level sections from nextflow_schema.json allOf order for chipseq

## Groups

- `input_output_options`: Preserves the original `nextflow_schema.json` top-level section `input_output_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Input/output options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/input_output_options.md`
  Asset: `assets/schema-groups/input_output_options.yaml`
- `reference_genome_options`: Preserves the original `nextflow_schema.json` top-level section `reference_genome_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Reference genome options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/reference_genome_options.md`
  Asset: `assets/schema-groups/reference_genome_options.yaml`
- `adapter_trimming_options`: Preserves the original `nextflow_schema.json` top-level section `adapter_trimming_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Adapter trimming options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/adapter_trimming_options.md`
  Asset: `assets/schema-groups/adapter_trimming_options.yaml`
- `alignment_options`: Preserves the original `nextflow_schema.json` top-level section `alignment_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Alignment options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/alignment_options.md`
  Asset: `assets/schema-groups/alignment_options.yaml`
- `peak_calling_options`: Preserves the original `nextflow_schema.json` top-level section `peak_calling_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Peak calling options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/peak_calling_options.md`
  Asset: `assets/schema-groups/peak_calling_options.yaml`
- `process_skipping_options`: Preserves the original `nextflow_schema.json` top-level section `process_skipping_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Process skipping options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/process_skipping_options.md`
  Asset: `assets/schema-groups/process_skipping_options.yaml`
- `institutional_config_options`: Preserves the original `nextflow_schema.json` top-level section `institutional_config_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Institutional config options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/institutional_config_options.md`
  Asset: `assets/schema-groups/institutional_config_options.yaml`
- `max_job_request_options`: Preserves the original `nextflow_schema.json` top-level section `max_job_request_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Max job request options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/max_job_request_options.md`
  Asset: `assets/schema-groups/max_job_request_options.yaml`
- `generic_options`: Preserves the original `nextflow_schema.json` top-level section `generic_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Generic options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/generic_options.md`
  Asset: `assets/schema-groups/generic_options.yaml`