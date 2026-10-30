# Playbooks

Use `assets/playbooks.yaml` as the exact route list. This reference explains the practical choice for each route.

## default_run

Use this for ordinary public accession runs. Put `input` and `outdir` under `nextflow_run(params=...)`. Leave `download_method` unset unless the user asks for a specific method; the schema default is `ftp`, and the workflow can route records without suitable FTP or Aspera links to sratools.

Expected review path:

- `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`
- `run_artifacts(...)` for samplesheet, fastq, metadata, and pipeline_info sections
- `fs_read(...)` only for explicit files such as `samplesheet/samplesheet.csv` or `pipeline_info/params.json`

## metadata_only

Use this when the user wants accession resolution, metadata, and samplesheet output without FASTQ downloads. Set `skip_fastq_download=true` under `params`. Missing `fastq/*.fastq.gz` files are expected for this route.

## sratools_download

Use this when the user asks for sratools, technical reads, more than two FASTQ files per sample, accessions without FTP links, or protected SRA data. Set `download_method=sratools` under `params`. For protected dbGaP data, also set `dbgap_key` to a server-local JWT file.

## aspera_download

Use this only when the user explicitly asks for Aspera. Set `download_method=aspera` under `params`. The source workflow only uses Aspera when ENA metadata includes Aspera links; otherwise records may be routed elsewhere by the workflow logic.

## downstream_samplesheet

Use this when the user wants a samplesheet for a downstream nf-core pipeline. Set `nf_core_pipeline` to one current enum value: `rnaseq`, `atacseq`, `viralrecon`, or `taxprofiler`. For `rnaseq`, the default `nf_core_rnaseq_strandedness` is `auto`; change it only when the user requests another value.

Warn the user to review the generated samplesheet before using it downstream. Public database metadata may not reliably contain all downstream fields, for example atacseq replicate information.

## Historical Reuse

When the user remembers only an output name fragment, search before guessing paths:

- `run_list(project=..., pipeline="fetchngs", artifact_path_contains=...)`
- `run_get(include=["artifact_summary"])` on candidate runs
- `run_artifacts(...)` for matching sections
- `fs_read(...)` for `pipeline_info/params.json` when route compatibility matters

Treat `artifacts.json` and `pipeline_fingerprint` as historical facts, then confirm compatibility through `pipeline_info/params.json`.
