# Troubleshooting

Start with `run_get(include=["progress","diagnosis","next_actions"])`. Use `run_logs()` only when
the structured summary is not enough. Use `fs_read()` only for one explicit file after the path is
known.

## Common Failures

## Samplesheet Or Path Errors

Check that `input` is server-local and that every `filename` inside the samplesheet is also
server-local. The expected columns are `sample`, `alleles`, `mhc_class`, and `filename`.

## Variant Annotation Errors

VCF input must be annotated with SnpEff or VEP. If epytope outputs are empty or missing, confirm
annotation source, `genome_reference`, optional `proteome_reference`, and VCF content.

## NetMHC Errors

If `tools` contains `netmhcpan`, `netmhcpan_path` must point to a server-local `.tar.gz`. If
`tools` contains `netmhciipan`, `netmhciipan_path` must point to a server-local `.tar.gz`. Confirm
the selected tarball and `netmhc_system` before rerunning.

## Missing Predictor Outputs

Missing predictor raw outputs can mean unsupported allele, unsupported peptide length, no peptides
left after filtering, or a NetMHC prerequisite failure. Review MultiQC, selected tools, MHC class,
and peptide length bounds.

## Restart

Use `from_run_id` as the public restart path. Read `run_get(detail="full")` on the source run when
`launch_spec`, `nextflow_session_uuid`, or resume compatibility matters. Do not pass public
Nextflow resume flags directly to `nextflow_run`.
