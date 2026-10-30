# Scope And Assumptions

This skill covers `nf-core/fetchngs` runs through nextmcp. The pipeline resolves SRA, ENA, DDBJ, and GEO accessions, fetches metadata, optionally downloads FASTQ files, and writes samplesheets for downstream use.

## Source Basis

- The authoring source is an inspect-equivalent bundle built from `nf_pipeline/fetchngs`.
- The bundle includes the current `nextflow_schema.json`, `README.md`, top-level docs, `main.nf`, and `nextflow.config`.
- Targeted source review also used `workflows/sra/main.nf` and module config files to confirm download routes and published outputs.

## Supported Routes

- `default_run`: FTP-first public data download plus metadata and samplesheet output.
- `metadata_only`: metadata and samplesheet output with `skip_fastq_download=true`.
- `sratools_download`: forced SRA Toolkit route with `download_method=sratools`.
- `aspera_download`: Aspera route when ENA metadata has Aspera links.
- `downstream_samplesheet`: samplesheet shaped for `rnaseq`, `atacseq`, `viralrecon`, or `taxprofiler`.
- `dbgap_sratools`: controlled-access SRA download with a server-local dbGaP JWT file.

## Runtime Boundaries

- Treat `pipeline="fetchngs"` as the default pipeline id route.
- Do not call `nextflow_inspect_pipeline` during ordinary runtime planning or launch.
- All runtime paths must already exist on the nextmcp server or come from nextmcp outputs.
- Use server-scoped placeholders such as `<server_input_root>/ids.csv` and `<server_output_root>/fetchngs` until the user or a nextmcp tool gives concrete paths.
- Use `from_run_id` for public restart planning. Do not teach `resume` or `resume_session_id` as `nextflow_run` inputs.
- Omit `profile` by default. Use the server default profile unless the user requests another runtime.
