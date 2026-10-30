# Outputs And QC

Start with `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`. Use
`run_artifacts(...)` before reading individual files. Use `fs_read(...)` only after a concrete path
is known.

## Review Order

1. Confirm the run succeeded and artifact summary contains the expected output families.
2. Review `pipeline_info/params.json` to confirm route, tools, and toggles.
3. Review `multiqc/multiqc_report.html` for prediction counts, score distributions, skipped
   unsupported alleles or peptide lengths, and versions.
4. Review `predictions/[sample].tsv` for final prediction results when `fasta_output` is false.
5. Review predictor raw output directories only when troubleshooting a specific tool.
6. Review `epytope/[sample].fasta` when `fasta_output` is true.

## Prediction Tables

Final prediction tables include the peptide column, `allele`, `BA`, `rank`, `binder`, `predictor`,
and source metadata. The docs advise selecting candidate binders based on `rank` for most
predictors. MHCnuggets has special rank caveats, so review `BA` for MHCnuggets-specific decisions.

`binder_only` changes table content by removing non-binders. `wide_format_output` changes table
shape by spreading predictor and allele metrics into separate columns.

## Historical Reuse

Use artifact fragments such as `predictions/`, `multiqc_report.html`, `pipeline_info/params.json`,
or `epytope/` with `run_list(..., artifact_path_contains=...)`. Confirm compatibility with
`pipeline_info/params.json` before recommending reuse or restart.
