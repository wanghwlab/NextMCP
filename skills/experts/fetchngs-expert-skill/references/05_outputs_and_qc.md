# Outputs And QC

Start with `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`. Use `run_artifacts(...)` next, then `fs_read(...)` only for explicit files.

## Main Outputs

- `fastq/*.fastq.gz`: downloaded reads when `skip_fastq_download=false`.
- `fastq/md5/*.md5`: md5 files for FTP or Aspera downloads.
- `samplesheet/samplesheet.csv`: main downstream handoff table.
- `samplesheet/id_mappings.csv`: public identifier to metadata mapping table.
- `samplesheet/multiqc_config.yml`: sample renaming config when `sample_mapping_fields` is set.
- `metadata/*.runinfo_ftp.tsv`: reformatted ENA metadata with download links and md5 fields.
- `pipeline_info/params.json`: launch parameters used for route confirmation and historical reuse.

## Review Order

1. Confirm the run completed and the artifact summary lists the expected sections.
2. Read `pipeline_info/params.json` when route choice matters, especially `download_method`, `skip_fastq_download`, `nf_core_pipeline`, and `dbgap_key`.
3. Inspect `samplesheet/samplesheet.csv` before launching downstream pipelines.
4. Inspect FASTQ and md5 artifacts only when a download run was expected.
5. For metadata-only runs, treat missing FASTQ files as expected and focus on samplesheet plus metadata outputs.

## QC Signals

- Good standard run: samplesheet, metadata, pipeline_info, and FASTQ artifacts are present.
- Good metadata-only run: samplesheet, metadata, and pipeline_info are present, and `params.json` confirms `skip_fastq_download=true`.
- Bad download run: no FASTQ files, md5 failures, or diagnosis output reporting transfer errors.
- Bad downstream handoff: samplesheet columns do not match the requested downstream pipeline or fields need manual curation.
