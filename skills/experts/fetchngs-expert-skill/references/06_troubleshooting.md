# Troubleshooting

- Start with `run_get(include=["progress","diagnosis","artifact_summary","next_actions"])`.
- Use `run_logs()` when the summary is not enough.
- Use `fs_read()` only for one explicit file after you know the path.
- Use `from_run_id` as the only public restart path when rerun planning matters.

## Common Cases

Missing input file:

- Confirm the server-local `input` path with `fs_list(mode="manifest")`.
- The schema expects `.csv`, `.tsv`, or `.txt` with one accession per line.

No FASTQ files:

- Read `pipeline_info/params.json`.
- If `skip_fastq_download=true`, this is expected for the metadata-only route.
- If FASTQ files were expected, inspect run logs for FTP, Aspera, sratools, or md5 failures.

More than two FASTQ files or technical reads expected:

- Plan a rerun with `download_method=sratools`.
- The source docs note that sratools may be the source of truth when ENA FTP metadata hides technical files.

dbGaP failures:

- Confirm `download_method=sratools`.
- Confirm `dbgap_key` points to a server-local JWT cart file.
- A 403 can mean the JWT is expired or was generated for only part of an experiment.

Downstream samplesheet concerns:

- Confirm `nf_core_pipeline` is one of `rnaseq`, `atacseq`, `viralrecon`, or `taxprofiler`.
- For `rnaseq`, confirm whether the default `nf_core_rnaseq_strandedness=auto` is acceptable.
- Tell the user to manually inspect fields that public databases may not provide reliably.
