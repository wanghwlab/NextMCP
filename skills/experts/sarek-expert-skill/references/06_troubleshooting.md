# Troubleshooting

Use the summary-first path: `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`,
then `run_logs` or `fs_read` only for concrete paths.

If launch validation fails, check `input`, `outdir`, and `step` first. The common cause is a
samplesheet that does not match the selected step. Mapping starts need lane and read columns.
Recalibrate starts need a recalibration table. Annotate starts need VCF rows.

If reference preparation fails, check paired files: FASTA with FAI and dict, VCF with TBI, PON with
TBI, dbNSFP with TBI, SpliceAI SNV/indel files with indexes, and ASCAT zip files. Use exact schema
lookup before renaming fields.

If tumor-normal outputs are missing, inspect samplesheet `patient`, `sample`, and `status` values.
Status `0` is normal and `1` is tumor. Pairing is source-driven and should not be fixed by changing
tools until metadata is checked.

If Sentieon fails, confirm the server-side `SENTIEON_LICENSE_BASE64` secret and required model
paths. Do not ask the user to paste the license string.

If annotation fails, check cache paths, species/genome/cache version fields, and plugin database
files. SnpEff chromosome mismatch often means the FASTA and SnpEff database do not match.

For restarts, use `from_run_id`. Read `run_get(detail="full")` on the source run when launch spec,
Nextflow session UUID, or resume compatibility matters.
