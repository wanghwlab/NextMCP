# Schema Lookup

The full current schema is preserved through grouped YAML assets. Do not scan the whole schema when
one group is enough.

## Lookup Flow

1. Open `assets/schema-index.yaml`.
2. Pick the group that matches the parameter.
3. Open `references/schema-groups/<group>.md` for a quick human-readable view.
4. Open `assets/schema-groups/<group>.yaml` when exact default, enum, channel, mapping flags, or
   hidden status matters.

## Groups

- `input_output_options`: samplesheet, outdir, email, MultiQC title.
- `reference_options`: genome and proteome references.
- `peptide_prediction_options`: peptide column, length bounds, predictor tools, wild-type
  prediction, FASTA-only output, wide output, and binder filtering.
- `run_optimisation`: VCF splitting and peptide chunking.
- `external_software`: NetMHC metadata, OS, and tarball paths.
- `institutional_config_options`: nf-core centralized config metadata.
- `generic_options`: publishing, MultiQC, help, validation, webhook, and version flags.

Every current schema parameter appears in exactly one grouped schema asset.
