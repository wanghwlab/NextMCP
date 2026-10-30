# Schema Lookup

- Grouping strategy: schema top-level sections from nextflow_schema.json allOf order for ampliseq

## Groups

- `input_output_options`: Preserves the original `nextflow_schema.json` top-level section `input_output_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Main arguments` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/input_output_options.md`
  Asset: `assets/schema-groups/input_output_options.yaml`
- `sequencing_input`: Preserves the original `nextflow_schema.json` top-level section `sequencing_input` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Sequencing input` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/sequencing_input.md`
  Asset: `assets/schema-groups/sequencing_input.yaml`
- `primer_removal`: Preserves the original `nextflow_schema.json` top-level section `primer_removal` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Primer removal` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/primer_removal.md`
  Asset: `assets/schema-groups/primer_removal.yaml`
- `read_trimming_and_quality_filtering`: Preserves the original `nextflow_schema.json` top-level section `read_trimming_and_quality_filtering` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Read trimming and quality filtering` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/read_trimming_and_quality_filtering.md`
  Asset: `assets/schema-groups/read_trimming_and_quality_filtering.yaml`
- `amplicon_sequence_variants_asv_calculation`: Preserves the original `nextflow_schema.json` top-level section `amplicon_sequence_variants_asv_calculation` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Amplicon Sequence Variants (ASV) calculation` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/amplicon_sequence_variants_asv_calculation.md`
  Asset: `assets/schema-groups/amplicon_sequence_variants_asv_calculation.yaml`
- `asv_post_processing`: Preserves the original `nextflow_schema.json` top-level section `asv_post_processing` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `ASV post processing` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/asv_post_processing.md`
  Asset: `assets/schema-groups/asv_post_processing.yaml`
- `taxonomic_assignment`: Preserves the original `nextflow_schema.json` top-level section `taxonomic_assignment` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Taxonomic assignment` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/taxonomic_assignment.md`
  Asset: `assets/schema-groups/taxonomic_assignment.yaml`
- `multiregion_taxonomic_database`: Preserves the original `nextflow_schema.json` top-level section `multiregion_taxonomic_database` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Multi-region taxonomic database` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/multiregion_taxonomic_database.md`
  Asset: `assets/schema-groups/multiregion_taxonomic_database.yaml`
- `asv_filtering`: Preserves the original `nextflow_schema.json` top-level section `asv_filtering` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `ASV filtering` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/asv_filtering.md`
  Asset: `assets/schema-groups/asv_filtering.yaml`
- `downstream_analysis`: Preserves the original `nextflow_schema.json` top-level section `downstream_analysis` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Downstream analysis` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/downstream_analysis.md`
  Asset: `assets/schema-groups/downstream_analysis.yaml`
- `differential_abundance_analysis`: Preserves the original `nextflow_schema.json` top-level section `differential_abundance_analysis` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Differential abundance analysis` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/differential_abundance_analysis.md`
  Asset: `assets/schema-groups/differential_abundance_analysis.yaml`
- `pipeline_report`: Preserves the original `nextflow_schema.json` top-level section `pipeline_report` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Pipeline summary report` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/pipeline_report.md`
  Asset: `assets/schema-groups/pipeline_report.yaml`
- `skipping_specific_steps`: Preserves the original `nextflow_schema.json` top-level section `skipping_specific_steps` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Skipping specific steps` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/skipping_specific_steps.md`
  Asset: `assets/schema-groups/skipping_specific_steps.yaml`
- `generic_options`: Preserves the original `nextflow_schema.json` top-level section `generic_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Generic options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/generic_options.md`
  Asset: `assets/schema-groups/generic_options.yaml`
- `institutional_config_options`: Preserves the original `nextflow_schema.json` top-level section `institutional_config_options` for exact lookup.
  Use when: The runtime agent needs exact parameter mapping for the `Institutional config options` top-level section of the current `nextflow_schema.json`.
  Reference: `references/schema-groups/institutional_config_options.md`
  Asset: `assets/schema-groups/institutional_config_options.yaml`