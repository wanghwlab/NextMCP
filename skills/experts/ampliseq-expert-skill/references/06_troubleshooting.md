# Troubleshooting

Start with `run_get(include=["progress","diagnosis","next_actions"])`. Use `run_logs()` only when the summary is not enough. Use `fs_read()` only for one explicit file after you know the path.

## Common Failure Routes

- Input errors: check exactly one of `input`, `input_folder`, or `input_fasta`; inspect samplesheet headers, compressed FASTQ extensions, sample IDs, and run columns.
- Primer trimming failures: check `FW_primer`, `RV_primer`, `double_primer`, `retain_untrimmed`, and `skip_cutadapt`.
- DADA2 sample loss: inspect `DADA2_stats.tsv`, quality profiles, `trunclen*`, `max_ee`, `min_len`, `max_len`, `illumina_novaseq`, `single_end`, `pacbio`, and `iontorrent`.
- Taxonomy failures: confirm database selector, custom database server path, classifier compatibility, and any license requirement.
- Sidle failures: confirm `multiregion` file columns and Sidle reference fields.
- Metadata failures: check the QIIME2 metadata format, `ID` column, category names, missing values, and formula fields.
- Resource failures: move caps into a server-local config file with `process.resourceLimits` and pass it through `config_files`.

## Restart

Use `from_run_id` as the public restart path. Read `run_get(detail="full")` on the source run when `launch_spec`, `nextflow_session_uuid`, or structured resume-compatibility fields matter. Do not use raw Nextflow resume flags as public `nextflow_run` inputs.
