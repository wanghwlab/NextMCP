# Troubleshooting

Start with `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`. Use
`run_logs` only when the summary does not explain the failure. Use `fs_read` only after a concrete
server-local file path is known.

If validation fails before launch, check `protocol`, `input`, `outdir`, demultiplexing fields, and
aligner choice. `protocol` must be `DNA`, `cDNA`, or `directRNA`; `aligner` must be `minimap2` or
`graphmap2`.

If demultiplexing fails, confirm `input_path` exists on the server, `barcode_kit` is supported, and
the samplesheet barcode values match the intended kit. When reads unexpectedly fall into
`none.fastq.gz`, review `barcode_both_ends`, `trim_barcodes`, `qcat_detect_middle`, and
`qcat_min_score`.

If NanoLyse fails in an offline environment, provide `nanolyse_fasta` explicitly or rerun without
`run_nanolyse`.

If alignment outputs are missing, check whether `skip_alignment=true` was set, whether samplesheet
`input_file` values are FASTQ or BAM as intended, and whether each row has the correct FASTA value.

If DNA variant outputs are missing, confirm `protocol=DNA`, `call_variants=true`, and the relevant
skip toggles. For `deepvariant` and `pepper_margin_deepvariant`, confirm Docker or Singularity. For
`deepvariant_gpu`, confirm the server has GPU scheduling configured outside ordinary params.

If quantification outputs are missing, confirm `protocol=cDNA` or `protocol=directRNA`,
`skip_quantification=false`, `quantification_method`, and samplesheet GTF values. For missing
differential results, also check `skip_differential_analysis` and whether groups/replicates are
represented in the samplesheet.

If RNA modification outputs are missing, confirm `protocol=directRNA`,
`skip_modification_analysis=false`, the `skip_xpore` and `skip_m6anet` values, successful alignment,
and the required `fast5` plus `fastq` directory layout for each sample.

If JAFFAL outputs are missing, confirm `protocol=cDNA` or `protocol=directRNA`,
`skip_fusion_analysis=false`, and either a valid server-local `jaffal_ref_dir` or server network
access to fetch the reference.

For restarts, use `from_run_id`. Read `run_get(detail="full")` on the source run when launch
specification, session UUID, or compatibility details matter.
