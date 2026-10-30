# Playbooks

Start with `assets/playbooks.yaml`. Choose a route before drafting the `nextflow_run` call.

For a normal RNA-seq run, use `star_salmon_default`. Confirm `project`, `input`, `outdir`, `fasta`,
and `gtf` or compatible pre-built indices. Use `nextflow_run(prepare=true)` when paths or run layout
need checking, then launch with `nextflow_run(pipeline="rnaseq", project=..., params=...)`.

Use `star_rsem_quantification` when the user asks for RSEM gene and isoform results. Keep source
BAM compatibility in mind: RSEM reruns should use BAMs from a STAR-RSEM route, not STAR-Salmon.

Use `hisat2_alignment_qc` when STAR memory is a problem or the user explicitly wants HISAT2. Tell
the user that this route does not produce expression quantification in this pipeline.

Use `pseudoalignment_only` for Salmon-only or Kallisto-only quantification. Set `skip_alignment:
true` and `pseudo_aligner`. Prefer a decoy-aware Salmon index for Salmon-only runs. For Kallisto
single-end input, check `kallisto_quant_fraglen` and `kallisto_quant_fraglen_sd`.

Use `bam_reprocessing` when reusing pipeline-generated BAMs. If the run id is unknown, search with
`run_list(artifact_path_contains="samplesheet_with_bams.csv")`, inspect candidates with
`run_get(include=["artifact_summary"])`, then use `run_artifacts` to locate
`pipeline_info/samplesheet_with_bams.csv` and `pipeline_info/params.json`.

Use `umi_run` when the user mentions UMIs. Confirm whether the UMI is in the read name or read
sequence. Use `skip_umi_extract` and `umitools_umi_separator` for read-name UMIs; use
`umitools_extract_method` and barcode patterns for sequence-embedded UMIs.

Use `filtering_and_contamination` for BBSplit, SortMeRNA, Kraken2, or Bracken. This route needs
server-local databases or manifests. Confirm licenses for Sentieon and SILVA-derived SortMeRNA
databases before launch when relevant.

The `interactive.nf` / `STEP_*` route is a custom extension, not a file shipped here
or guaranteed by an official release. Use `interactive_entry` only when the user
asks for a single exploratory step and the matching extension is confirmed installed.
Otherwise report that this optional route is unavailable. Resolve the
server-local pipeline root if needed, pass the entry as `extra_args: ["-entry", "<STEP_NAME>"]`,
and provide only the entry-specific params.

After launch, start with
`run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`. Use `run_artifacts`
for named output sections, `run_logs` for Nextflow stdout/stderr, and `fs_read` only after a
specific file path is known.
