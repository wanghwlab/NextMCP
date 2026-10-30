# Schema Lookup

The compact parameter guide does not list all 173 parameters. Exact lookup lives in
`assets/schema-index.yaml` and `assets/schema-groups/*.yaml`.

Use this sequence:

1. Open `assets/schema-index.yaml`.
2. Find the parameter name or the matching top-level group.
3. Open only the matching `assets/schema-groups/<group>.yaml` file.
4. Use the grouped record for type, default, enum choices, required status, channel, placeholder,
   mapping notes, confidence, and mapping flags.

The schema groups preserve the pipeline's own top-level section structure, including
`input_output_options`, `quality_control_for_short_reads_options`,
`quality_control_for_long_reads_options`, `assembly_options`, `binning_options`,
`bin_quality_check_options`, `taxonomic_profiling_options`,
`gene_prediction_and_annotation_options`, `virus_identification_options`,
`ancient_dna_assembly`, `reproducibility_options`, `reference_genome_options`,
`generic_options`, and `institutional_config_options`.

Use grouped lookup whenever the user mentions a specific parameter, asks whether a value is valid,
or asks for a less common switch. For example, use grouped lookup for `adapterremoval_trim_quality_stretch`,
`bin_metabinner_scale`, `postbinning_input`, `gtdbtk_skip_aniscreen`,
`metaeuk_mmseqs_db`, or `bcftools_view_high_variant_quality`.
