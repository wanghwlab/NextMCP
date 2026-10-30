# Outputs and QC

Start post-run review with `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`. Use `run_artifacts(...)` for relevant sections, then `fs_read` only for explicit report or table paths.

## Review Order

1. `multiqc/<aligner>/multiqc_report.html`: main summary report when `skip_multiqc=false`.
2. `pipeline_info/params.json`: route, reference, and option record for reuse and troubleshooting.
3. Route-specific alignment and methylation outputs.
4. Optional QC or target outputs only when requested.

## Route-Specific Outputs

Bismark routes publish `bismark/alignments`, `bismark/deduplicated`, `bismark/methylation_calls`, `bismark/reports`, and `bismark/summary`.

BWA-Meth publishes `bwameth/alignments`, `bwameth/deduplicated`, and MethylDackel outputs under `methyldackel`, including bedGraph and M-bias files. `all_contexts`, `merge_context`, and `methyl_kit` change the output shape.

BWA-MEM/TAPS publishes `bwamem/alignments`, `bwamem/deduplicated`, and Rastair outputs under `rastair/call`, `rastair/mbias`, `rastair/mbiasparser`, and `rastair/methylkit`.

Targeted sequencing publishes filtered `*targeted.bedGraph` files and optional `enrichment_metrics` when `collecthsmetrics=true`.

Saved intermediates appear only when requested by `save_trimmed`, `save_align_intermeds`, `unmapped`, `save_reference`, `skip_deduplication`, or `rrbs`.

## QC Rules

Use `assets/qc-rules.yaml` as the primary checklist. Key checks are:

- Confirm samplesheet and all paths resolve on the nextmcp server filesystem.
- Confirm the selected aligner has matching reference inputs.
- Check route compatibility before launch, especially TAPS plus targeted sequencing.
- Compare raw and trimmed read QC in MultiQC.
- Review alignment and deduplication logs for route-specific failures.
- Confirm methylation caller outputs and M-bias files are present.
- For historical reuse, treat `artifacts.json` and `pipeline_fingerprint` as facts, then confirm route compatibility with `pipeline_info/params.json`.
