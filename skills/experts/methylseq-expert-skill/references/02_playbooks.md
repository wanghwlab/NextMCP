# Playbooks

Start from `assets/playbooks.yaml`; this file gives the same routes in prose.

## Bismark Default

Use `bismark_default` for ordinary bisulfite sequencing. Confirm `project`, `input`, `outdir`, `aligner=bismark`, and a reference source. A configured genome can resolve references; otherwise provide `fasta` plus `bismark_index`. If the run builds a reference that should be reused, set `save_reference=true`.

Review MultiQC first, then Bismark alignments, deduplication logs, methylation calls, reports, summary, and `pipeline_info/params.json`.

## Bismark-HISAT2 and SLAM-seq

Use `bismark_hisat_slamseq` when the user asks for HISAT2, splice-aware alignment, or SLAM-seq. Set `aligner=bismark_hisat`. Use `known_splices` for splice-aware alignment and `slamseq=true` only when requested.

## BWA-Meth

Use `bwameth_methyldackel` for BWA-Meth with MethylDackel. Confirm `fasta`, `fasta_index`, and `bwameth_index`, unless the configured genome supplies them. Set `use_mem2=true` only when the user asks for BWA-MEM2.

For GPU acceleration, keep `aligner=bwameth`, confirm the server supports a GPU profile, and pass `profile` only when requested or when the server default is unsuitable. Do not choose Conda or Mamba for this route.

## TAPS and BWA-MEM

Use `taps_bwamem_rastair` for TAPS or BWA-MEM routes. Prefer `aligner=bwamem` and set `taps=true` for TAPS libraries. This route publishes `rastair/call`, `rastair/mbias`, `rastair/mbiasparser`, and `rastair/methylkit`.

Do not combine `run_targeted_sequencing` with TAPS or `aligner=bwamem`; the workflow errors because targeted mode does not run with Rastair.

## Special Libraries

Use `special_library_preset` when the user names PBAT, RRBS, single-cell bisulfite, Accel, Zymo, EM-seq, NOMe-seq, or NMT-seq. These flags can change trimming, strand handling, deduplication, and methylation context output. Use `skip_trimming_presets=true` only when the user wants to manage clipping manually.

## Targeted Sequencing

Use `targeted_sequencing` for region-focused methylation analysis. Set `run_targeted_sequencing=true` and provide `target_regions_file`. Set `collecthsmetrics=true` only when hybrid-selection metrics are requested.

## Tool Order

Use this order unless the user has already supplied the missing facts:

1. `project_list()` if the project id is unknown.
2. `project_get(project)` if the project root or previous runs matter.
3. `fs_list(mode="manifest")` for a concrete server-local samplesheet, reference, target BED, or outdir path that needs confirmation.
4. `nextflow_run(prepare=true)` when launch layout or inputs still need checking.
5. `nextflow_run(pipeline="methylseq", project=..., params=...)` to launch.
6. `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])` after launch.
7. `run_artifacts(...)` before reading individual reports or result files.

For historical reuse, use `run_list(project=..., pipeline="methylseq", artifact_path_contains=...)`, then `run_get(include=["artifact_summary"])`, then `run_artifacts(...)`. Confirm compatibility with `pipeline_info/params.json`.
