# Parameters

Use this compact guide for planning. Use `assets/schema-index.yaml` and the grouped schema assets
when an exact type, default, enum, or hidden parameter matters.

## Required Params

- `input`: server-local samplesheet path.
- `outdir`: server-local result directory.

Both belong under `nextflow_run(params=...)`, not top-level arguments.

## Route-Shaping Params

- `tools`: comma-separated predictor list. Valid values are `mhcflurry`, `mhcnuggets`,
  `mhcnuggetsii`, `netmhcpan`, and `netmhciipan`.
- `genome_reference`: `grch37`, `grch38`, or an Ensembl BioMart archive URL for variant input.
- `proteome_reference`: server-local FASTA used for self-filtering variant-derived peptides.
- `min_peptide_length_classI`, `max_peptide_length_classI`,
  `min_peptide_length_classII`, `max_peptide_length_classII`: peptide length filters.
- `peptide_col_name`: peptide sequence column for TSV input, default `sequence`.
- `fasta_output`: FASTA-only variant output. Skips binding prediction.
- `wide_format_output`: wide final result table.
- `binder_only`: keep only peptides predicted as binders by at least one predictor.
- `split_by_variants`, `split_by_variants_size`, `split_by_variants_distance`: large VCF split
  behavior.
- `netmhcpan_path`, `netmhciipan_path`: required server-local tarballs when the matching NetMHC
  predictor is selected.
- `netmhc_system`: `linux` or `darwin`, usually left as `linux`.

## nextmcp Boundaries

- `project`: top-level `nextflow_run` argument.
- `params`: ordinary pipeline options listed above.
- `config_files`: Nextflow config files and resource caps.
- `from_run_id`: only public restart path.
- `extra_args`: only when no normalized field covers a needed CLI flag.

Omit `profile` by default and use the server default profile unless the user requests otherwise.

## Exact Lookup

Use `assets/schema-index.yaml` to choose a group:

- `input_output_options`: `input`, `outdir`, email, MultiQC title.
- `reference_options`: `genome_reference`, `proteome_reference`.
- `peptide_prediction_options`: predictor selection, peptide lengths, FASTA/wide/binder toggles.
- `run_optimisation`: splitting and chunking.
- `external_software`: NetMHC paths and OS selection.
- `institutional_config_options`: nf-core institutional config metadata.
- `generic_options`: nf-core reporting, help, validation, and notification fields.
