# Troubleshooting

Start with `run_get(include=["progress","diagnosis","next_actions"])`. Use `run_logs()` only when the summary does not explain the failure. Use `fs_read()` only for one explicit log, report, or output file path.

## Common Failures

- `protocol=auto` with Simpleaf, STARsolo, or Kallisto/BUS: choose a concrete protocol and rerun.
- Missing or incompatible reference: confirm `simpleaf_index`, `star_index`, `kallisto_index`, `cellranger_index`, `cellranger_vdj_index`, FASTA/GTF, or Cell Ranger ARC config paths on the server.
- Cell Ranger runtime missing: confirm the server profile includes the licensed tool before launch.
- Cell Ranger ARC FASTQ naming mismatch: the ARC route expects 10x-compatible FASTQ names.
- Cell Ranger Multi metadata mismatch: check `feature_type`, barcode samplesheet, FFPE probe set, feature reference, and VDJ reference choices.
- Missing expected output: check whether `skip_fastqc`, `skip_multiqc`, `skip_cellbender`, `save_reference`, or `save_align_intermeds` changed the output set.

## Restart

For restart planning, inspect the source run with `run_get(detail="full")` so the agent can see `launch_spec`, `nextflow_session_uuid`, and structured resume-compatibility fields. Use `from_run_id` as the public restart path. Do not teach legacy raw resume flags as public `nextflow_run` inputs.
