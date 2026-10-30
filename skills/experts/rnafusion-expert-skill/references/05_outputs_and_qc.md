# Outputs And QC

Use `assets/artifact-contracts.yaml` for exact output families and `assets/qc-rules.yaml` for
review checks.

## Summary-First Review

Start with:

```text
run_get(include=["progress","artifact_summary","diagnosis","next_actions"])
```

If the run succeeded, call `run_artifacts(...)` for the relevant sections. Use `fs_read` only for
explicit files returned by artifact metadata or a manifest.

## Review Order

1. `pipeline_info/params_<timestamp>.json`: confirm tools, references, skip flags, and route.
2. `fusionreport/<sample>/<sample>.fusionreport_filtered.tsv` and HTML index: main cross-caller
   summary. Interpret Fusion Indication Index with the active tools and database availability.
3. `fusioninspector/<sample>/<sample>.FusionInspector.fusions.tsv` and web report: supervised
   evidence review for candidate fusions.
4. Caller outputs: `arriba`, `starfusion`, and `fusioncatcher` directories.
5. `vcf/<sample>_fusion_data.vcf` when VCF creation was enabled.
6. `multiqc/multiqc_report.html`, FastQC, fastp, and Picard metrics when QC was enabled.
7. STAR BAM/CRAM, junctions, splice junctions, Salmon, StringTie, and CTAT-SPLICING outputs when
   those route pieces were selected.

## Historical Reuse

When the user remembers only an output filename fragment, search with
`run_list(project=..., pipeline="rnafusion", artifact_path_contains=...)`. Then inspect
`run_get(include=["artifact_summary"])` and `run_artifacts(...)`. Treat `artifacts.json` and
`pipeline_fingerprint` as historical facts. Confirm compatibility through
`pipeline_info/params_<timestamp>.json` or equivalent run metadata before recommending reuse.
