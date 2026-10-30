# Troubleshooting

Start with `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`. Use `run_logs` only when the summary does not explain the failure. Use `fs_read` only after you have an explicit server-local log, report, or output path.

## Common Failures

Missing input or reference path:
Confirm the samplesheet, FASTQ paths, FASTA, FASTA index, aligner index, and target BED are server-local paths. Use `fs_list(mode="manifest")` on the concrete path.

Wrong reference for route:
Bismark needs a Bismark index or a buildable FASTA. BWA-Meth needs `fasta`, `fasta_index`, and `bwameth_index`. BWA-MEM/TAPS needs `fasta`, `fasta_index`, and `bwamem_index`.

Targeted sequencing fails:
Confirm `run_targeted_sequencing=true` and `target_regions_file` are set. Do not use targeted mode with TAPS or `aligner=bwamem`.

SLAM-seq fails:
Use `aligner=bismark_hisat` with `slamseq=true`. Confirm `known_splices` only when splice-aware alignment is requested.

Unexpected trimming or strand behavior:
Check special library flags. `pbat`, `single_cell`, `accel`, `zymo`, and `em_seq` change trimming presets unless `skip_trimming_presets=true`. `single_cell` and `zymo` also imply non-directional Bismark behavior. `rrbs` skips deduplication by design.

Missing MultiQC:
Check `skip_multiqc`. If the run failed before final aggregation, use route-specific logs and then rerun or restart with `from_run_id`.

Restart planning:
Use `run_get(detail="full")` on the source run when `launch_spec`, `nextflow_session_uuid`, or restart compatibility matters. Launch with `nextflow_run(from_run_id=...)`.

Historical output lookup:
Use `run_list(project=..., pipeline="methylseq", artifact_path_contains=...)` with fragments such as `multiqc_report.html`, `pipeline_info/params.json`, `methyldackel`, `rastair/call`, or `targeted.bedGraph`. Then inspect `run_get(include=["artifact_summary"])` and `run_artifacts(...)`.
