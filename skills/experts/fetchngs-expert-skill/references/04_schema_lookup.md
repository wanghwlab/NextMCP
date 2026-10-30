# Schema Lookup

- Grouping strategy: schema top-level sections from nextflow_schema.json allOf order for fetchngs

## Groups

- `input_output_options`: Preserves the original `nextflow_schema.json` top-level section `input_output_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Input/output options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/input_output_options.md`
  Asset: `assets/schema-groups/input_output_options.yaml`
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
- `deprecated_options`: Preserves the original `nextflow_schema.json` top-level section `deprecated_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Deprecated options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/deprecated_options.md`
  Asset: `assets/schema-groups/deprecated_options.yaml`