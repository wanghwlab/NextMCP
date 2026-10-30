# Post variant calling

The runtime agent needs exact parameter mapping for the `Post variant calling` top-level section of the current `nextflow_schema.json`.

Use this group for parameters defined under the `Post variant calling` top-level schema section.

- Exact source: `assets/schema-groups/post_variant_calling.yaml`
- Discovery index: `assets/schema-index.yaml`

## Route-shaping

- `concatenate_vcfs`
- `filter_vcfs`
- `normalize_vcfs`
- `snv_consensus_calling`

## Lookup-only

- `bcftools_filter_criteria`
- `consensus_min_count`
- `varlociraptor_chunk_size`
- `varlociraptor_scenario_germline`
- `varlociraptor_scenario_somatic`
- `varlociraptor_scenario_tumor_only`

## Non-runtime

No non-runtime or authoring-only parameters were classified into this group.
