# Parameters

Use `assets/param-presets.yaml` first. Replace every placeholder with a server-local value.

## Required Inputs

- `input`: File containing SRA/ENA/GEO/DDBJ identifiers one per line to download their associated metadata and FastQ files.
  Placeholder: `<server_input_root>/ids.csv`
- `outdir`: Server-local output directory for FASTQ files, metadata, samplesheets, and pipeline_info reports.
  Placeholder: `<server_output_root>/fetchngs`

## Route-Shaping Params

- `download_method`: enum `ftp`, `sratools`, or `aspera`; default is `ftp`.
- `skip_fastq_download`: set `true` for metadata and samplesheet output without FASTQ downloads.
- `nf_core_pipeline`: enum `rnaseq`, `atacseq`, `viralrecon`, or `taxprofiler`; changes samplesheet columns for downstream use.
- `nf_core_rnaseq_strandedness`: applies when `nf_core_pipeline=rnaseq`; default is `auto`.
- `dbgap_key`: server-local JWT cart file for protected dbGaP data. Use with `download_method=sratools`.
- `ena_metadata_fields`: optional comma-separated ENA fields. Keep the required fields `run_accession,experiment_accession,library_layout,fastq_ftp,fastq_md5`.
- `sample_mapping_fields`: optional comma-separated fields used to create `id_mappings.csv` and `multiqc_config.yml`.

## Channel Boundaries

Put ordinary pipeline options under `nextflow_run(params=...)`: `input`, `outdir`, `download_method`, `skip_fastq_download`, `nf_core_pipeline`, `nf_core_rnaseq_strandedness`, `dbgap_key`, `ena_metadata_fields`, and `sample_mapping_fields`.

Put Nextflow config files and resource caps in `nextflow_run(config_files=[...])`.
For this nf-core pipeline, resource caps should use:

```groovy
process {
  resourceLimits = [cpus: 8, memory: '32.GB', time: '24.h']
}
```

Do not invent `params.max_cpus`, `params.max_memory`, `params.max_time`, or
`process.maxCpus`.

Use `from_run_id` for restart planning. Inspect `run_get(detail="full")` on the source run when the launch spec, Nextflow session UUID, or resume compatibility matters.

## Exact Lookup

- Use `assets/schema-index.yaml` to choose the right schema group.
- Open the matching grouped reference before the YAML when that is enough.
- Open `assets/schema-groups/input_output_options.yaml` for exact enum values and descriptions for the main fetchngs route-shaping parameters.
- Open `assets/schema-groups/max_job_request_options.yaml` before rendering resource-cap override configs.
