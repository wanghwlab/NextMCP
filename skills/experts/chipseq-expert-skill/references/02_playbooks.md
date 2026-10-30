# Playbooks

## default_run

Use for a standard ChIP-seq run. The default is `aligner: bwa` and broad MACS3 peak
calling. Confirm the nextmcp `project`, server-local samplesheet, `outdir`, and
either `genome` or `fasta` plus `gtf` or `gff`.

Prerequisites:
- Confirm `input` on the nextmcp server with `fs_list(mode="manifest")` when the
  path is uncertain.
- Confirm the samplesheet first seven columns: `sample`, `fastq_1`, `fastq_2`,
  `replicate`, `antibody`, `control`, `control_replicate`.
- Confirm `outdir` on the nextmcp server.
- Confirm `genome`, or confirm server-local `fasta` and `gtf` or `gff`.
- Prefer prebuilt indices for large genomes; set `save_reference` if the pipeline
  should keep generated indices.

- Preset: `default_run`

Tool order:
1. `server_info()` if the default profile or server layout is unknown.
2. `project_list()` or `project_get(project)` when project identity or prior runs
   matter.
3. `fs_list(path=..., mode="manifest")` for uncertain input, reference, or index
   paths.
4. `nextflow_run(prepare=true, pipeline="chipseq", project=..., params=...)` when
   launch layout still needs checking.
5. `nextflow_run(pipeline="chipseq", project=..., params=...)`.
6. `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`.

## narrow_peak

Use when the user asks for transcription factor peaks, narrowPeak outputs, or MACS3
narrow mode. Set `narrow_peak: true` in `params`. Review
`<ALIGNER>/merged_library/macs3/narrowPeak/`, `multiqc/narrowPeak/`, and
`igv/narrowPeak/`.

## alternate_aligner

Use when the user requests `bwa`, `bowtie2`, `chromap`, or `star`, wants unmapped
reads, or wants aligner comparison. Map `aligner` exactly to the schema enum. Confirm
the matching index path when available. `save_unaligned` only applies to Bowtie2 and
STAR. Downstream outputs are placed under the selected `<ALIGNER>/` directory, which
lets users compare runs by changing aligner and restarting safely with `from_run_id`
or by launching a separate run.

## saved_handoff_outputs

Use when the user needs intermediate files. Set only the save flags the user needs:
`save_trimmed`, `save_align_intermeds`, `save_unaligned`, or `save_macs_pileup`.
Warn that these increase output size. The main handoff paths are `trimgalore/`,
`<ALIGNER>/library/`, `<ALIGNER>/library/unmapped/`, and
`<ALIGNER>/merged_library/macs3/<PEAK_TYPE>/`.

## qc_light_run

Use only when the user explicitly accepts missing QC. Skip flags can remove FastQC,
Preseq, SPP, plotFingerprint, plotProfile, IGV, MultiQC, peak QC, annotation,
consensus peaks, or DESeq2 QC. Keep MultiQC unless the user specifically asks to skip
it, because it is the main review entry point.

## historical_reuse_or_restart

When the user remembers only an output fragment, use
`run_list(project=..., pipeline="chipseq", artifact_path_contains=...)`. Then inspect
`run_get(include=["artifact_summary"])` and `run_artifacts(...)`. Treat
`artifacts.json` and `pipeline_fingerprint` as historical facts, then confirm
compatibility through `pipeline_info/params.json` before recommending reuse. Use
`from_run_id` as the public restart path.
