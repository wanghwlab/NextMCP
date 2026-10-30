# Outputs And QC

Start with `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`. Then use `run_artifacts(...)` for the relevant section and `fs_read(...)` only after a concrete server-local path is known.

## Review Order

1. `pipeline_info/params.json`: confirm route, references, protocol, and skip/save flags.
2. `multiqc/multiqc_report.html`: review aggregated QC when MultiQC was not skipped.
3. Selected aligner output family: `simpleaf/`, `star/`, `kallisto/`, `cellranger/`, `cellrangerarc/`, or `cellrangermulti/`.
4. Matrix handoff files under `<aligner>/mtx_conversions/`.
5. CellBender outputs when the route includes remove-background filtering.

## Important Output Meanings

Simpleaf publishes quantification folders and AlevinQC HTML reports. STARsolo publishes per-sample STAR outputs and optional BAMs. Kallisto/BUS publishes raw/sorted BUS data, count matrices, and metrics. Cell Ranger routes publish web summaries, matrices, and count outputs. Cell Ranger Multi adds aggregate `multi` outputs plus `per_sample_outs` for demultiplexed samples.

Matrix conversion suffixes matter: `raw`, `filtered`, and `cellbender_filter` describe provenance. Preserve those suffixes when handing files to downstream analysis.

## Historical Reuse

When the user remembers one output fragment, search with `run_list(project=..., pipeline="scrnaseq", artifact_path_contains=...)`. Treat `artifacts.json` and `pipeline_fingerprint` as historical facts. Read `pipeline_info/params.json` before saying an old matrix, report, or reference is compatible with the new request.
