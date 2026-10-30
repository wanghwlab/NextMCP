# Schema Lookup

- Grouping strategy: schema top-level sections from nextflow_schema.json allOf order for sarek

## Groups

- `input_output_options`: Preserves the original `nextflow_schema.json` top-level section `input_output_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Input/output options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/input_output_options.md`
  Asset: `assets/schema-groups/input_output_options.yaml`
- `main_options`: Preserves the original `nextflow_schema.json` top-level section `main_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Main options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/main_options.md`
  Asset: `assets/schema-groups/main_options.yaml`
- `fastq_preprocessing`: Preserves the original `nextflow_schema.json` top-level section `fastq_preprocessing` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `FASTQ Preprocessing` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/fastq_preprocessing.md`
  Asset: `assets/schema-groups/fastq_preprocessing.yaml`
- `umi_processing`: Preserves the original `nextflow_schema.json` top-level section `umi_processing` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Unique Molecular Identifiers` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/umi_processing.md`
  Asset: `assets/schema-groups/umi_processing.yaml`
- `preprocessing`: Preserves the original `nextflow_schema.json` top-level section `preprocessing` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Preprocessing` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/preprocessing.md`
  Asset: `assets/schema-groups/preprocessing.yaml`
- `variant_calling`: Preserves the original `nextflow_schema.json` top-level section `variant_calling` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Variant Calling` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/variant_calling.md`
  Asset: `assets/schema-groups/variant_calling.yaml`
- `post_variant_calling`: Preserves the original `nextflow_schema.json` top-level section `post_variant_calling` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Post variant calling` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/post_variant_calling.md`
  Asset: `assets/schema-groups/post_variant_calling.yaml`
- `annotation`: Preserves the original `nextflow_schema.json` top-level section `annotation` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Annotation` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/annotation.md`
  Asset: `assets/schema-groups/annotation.yaml`
- `general_reference_genome_options`: Preserves the original `nextflow_schema.json` top-level section `general_reference_genome_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `General reference genome options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/general_reference_genome_options.md`
  Asset: `assets/schema-groups/general_reference_genome_options.yaml`
- `reference_genome_options`: Preserves the original `nextflow_schema.json` top-level section `reference_genome_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Reference genome options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/reference_genome_options.md`
  Asset: `assets/schema-groups/reference_genome_options.yaml`
- `institutional_config_options`: Preserves the original `nextflow_schema.json` top-level section `institutional_config_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Institutional config options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/institutional_config_options.md`
  Asset: `assets/schema-groups/institutional_config_options.yaml`
- `generic_options`: Preserves the original `nextflow_schema.json` top-level section `generic_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Generic options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/generic_options.md`
  Asset: `assets/schema-groups/generic_options.yaml`