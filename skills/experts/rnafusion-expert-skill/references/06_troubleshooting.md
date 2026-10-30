# Troubleshooting

Start with `run_get(include=["progress","diagnosis","next_actions","artifact_summary"])`. Use
raw logs only after the summary points to a process, file, or Nextflow error.

## Missing References

If the error mentions missing `fusioncatcher_ref`, Arriba reference files, STAR-Fusion reference,
database files, or index files, confirm `genomes_base` with `fs_list(mode="manifest")`. Build or
download references before rerunning. For reference building, use `references_only=true`.

## COSMIC Or Database Problems

If COSMIC credentials or license coverage are unavailable, use the no-COSMIC route. If the user has
QIAGEN credentials, set `qiagen=true` only when they confirm that provider. Do not invent or store
credentials.

## FusionInspector Has No Input

FusionInspector needs a provided `fusioninspector_fusions` file or valid upstream caller output
through fusion-report with visualization enabled. If `skip_vis=true` and no fusion list is
provided, the workflow can fail because FusionInspector has no valid fusion input.

## Samplesheet Does Not Support Selected Tools

The workflow may align reads when selected tools need BAM, CRAM, junctions, or splice junctions.
If alignment is needed but no FASTQ files are present, provide FASTQ files or provide the required
aligned files and junction files for the selected tools.

## Conda Or Mamba With CTAT-SPLICING

The workflow rejects Conda or Mamba when `ctatsplicing` is selected. Omit `profile` by default or
use a supported container runtime if the user asks for one.

## FusionCatcher Long Reads

FusionCatcher is sensitive to read length. For reads above 100 bp, consider `fastp` plus
`trim_tail_fusioncatcher` so FusionCatcher receives shorter reads.

## Restart Planning

Use `nextflow_run(from_run_id=...)` for the public restart path. Before recommending a restart,
inspect the source run with `run_get(detail="full")` when `launch_spec`,
`nextflow_session_uuid`, or structured resume compatibility fields matter.
