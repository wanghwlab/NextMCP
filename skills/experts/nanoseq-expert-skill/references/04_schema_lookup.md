# Schema Lookup

- Grouping strategy: schema top-level sections from nextflow_schema.json allOf order for nanoseq

## Groups

- `input_output_options`: Preserves the original `nextflow_schema.json` top-level section `input_output_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Input/output options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/input_output_options.md`
  Asset: `assets/schema-groups/input_output_options.yaml`
- `demultiplexing_options`: Preserves the original `nextflow_schema.json` top-level section `demultiplexing_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Demultiplexing options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/demultiplexing_options.md`
  Asset: `assets/schema-groups/demultiplexing_options.yaml`
- `alignment_options`: Preserves the original `nextflow_schema.json` top-level section `alignment_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Alignment options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/alignment_options.md`
  Asset: `assets/schema-groups/alignment_options.yaml`
- `variant_calling_options`: Preserves the original `nextflow_schema.json` top-level section `variant_calling_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Variant calling options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/variant_calling_options.md`
  Asset: `assets/schema-groups/variant_calling_options.yaml`
- `differential_analysis_options`: Preserves the original `nextflow_schema.json` top-level section `differential_analysis_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Differential analysis options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/differential_analysis_options.md`
  Asset: `assets/schema-groups/differential_analysis_options.yaml`
- `rna_fusion_analysis_options`: Preserves the original `nextflow_schema.json` top-level section `rna_fusion_analysis_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `RNA fusion analysis options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/rna_fusion_analysis_options.md`
  Asset: `assets/schema-groups/rna_fusion_analysis_options.yaml`
- `rna_modification_analysis_options`: Preserves the original `nextflow_schema.json` top-level section `rna_modification_analysis_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `RNA modification analysis options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/rna_modification_analysis_options.md`
  Asset: `assets/schema-groups/rna_modification_analysis_options.yaml`
- `process_skipping_options`: Preserves the original `nextflow_schema.json` top-level section `process_skipping_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Process skipping options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/process_skipping_options.md`
  Asset: `assets/schema-groups/process_skipping_options.yaml`
- `reference_genome_options`: Preserves the original `nextflow_schema.json` top-level section `reference_genome_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Reference genome options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/reference_genome_options.md`
  Asset: `assets/schema-groups/reference_genome_options.yaml`
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