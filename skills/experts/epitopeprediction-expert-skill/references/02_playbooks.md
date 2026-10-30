# Playbooks

Start from `assets/playbooks.yaml` for exact route IDs and presets.

## Standard Prediction

Use `standard_prediction` for annotated variants, protein FASTA, or peptide TSV. Confirm the
server-local samplesheet and every `filename` path inside it. For VCF input, confirm SnpEff or VEP
annotation before launch.

Default launch shape:

```yaml
pipeline: epitopeprediction
project: <project>
params:
  input: <server_input_root>/samplesheet.csv
  outdir: <server_output_root>/epitopeprediction
  tools: mhcnuggets
```

## NetMHC Prediction

Use `netmhc_prediction` when `tools` includes `netmhcpan` or `netmhciipan`. The matching path
parameter is required. Confirm it is a server-local `.tar.gz` path before launch.

```yaml
params:
  tools: netmhcpan,netmhciipan
  netmhcpan_path: <server_software_root>/netMHCpan-4.1b.Linux.tar.gz
  netmhciipan_path: <server_software_root>/netMHCIIpan-4.3e.Linux.tar.gz
```

Only set `netmhc_system` when the server runtime makes the default `linux` value wrong.

## FASTA-Only Variant Output

Use `fasta_only_variant_output` when the user wants variant protein FASTA output, for example as
handoff to another workflow. Set `fasta_output: true`. This route skips MHC binding prediction, so
do not promise `predictions/[sample].tsv`.

## Reporting Shape

Use `reporting_shape` when the user asks for:

- `binder_only`: drop non-binders from final prediction tables
- `wide_format_output`: spread predictor and allele metrics into separate columns
- `multiqc_methods_description`: use a server-local YAML file for custom methods text

## Large VCF Splitting

Use `variant_split_optimisation` only for VCF or VCF.GZ input when the user has a scaling reason.
Set `split_by_variants: true`, then tune `split_by_variants_size` or
`split_by_variants_distance` only when needed.

## Historical Reuse

When the user remembers only an output fragment, search with
`run_list(project=..., pipeline="epitopeprediction", artifact_path_contains=...)`. Good fragments
include `predictions/`, `multiqc_report.html`, `pipeline_info/params.json`, and `epytope/`.

Then inspect `run_get(include=["artifact_summary"])`, use `run_artifacts(...)`, and confirm route
compatibility through `pipeline_info/params.json`. Treat `artifacts.json` and
`pipeline_fingerprint` as historical facts, not proof that reuse is safe.
