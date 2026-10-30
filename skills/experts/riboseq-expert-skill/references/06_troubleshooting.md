# Troubleshooting

Start with `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`. Use
`run_logs` only when the summary does not identify the failing process. Use `fs_read` for explicit
logs or outputs after their server-local paths are known.

If input validation fails, check the samplesheet first five columns, server-local FASTQ paths,
gzip extensions, duplicate sample naming for resequenced lanes, and the `type` values. Use
`extra_fqlint_args` only for a known fq validator issue.

If strandedness fails, inspect the MultiQC strandedness table. Correct the samplesheet
`strandedness` values or threshold parameters before trusting quantification.

If STAR fails or mapping is low, confirm the FASTA/GTF pair, GENCODE mode, STAR index compatibility,
read trimming, and resource limits. Large references may need a `config_files` override with
`process.resourceLimits`.

If BAM indexing fails on large references, rerun with `bam_csi_index` true.

If SortMeRNA fails, confirm `ribo_database_manifest` or `sortmerna_index` and license suitability
for the database source.

If BBSplit is expected but absent, remember that `skip_bbsplit` defaults to skipping the step. Set
it false and provide `bbsplit_fasta_list` or `bbsplit_index`.

If UMI outputs are missing, confirm `with_umi` and whether extraction should be skipped. UMIs in
read names need a separator; UMIs in sequence need an exact regex pattern.

If Ribo-TISH or Ribotricer outputs are missing, check `skip_ribotish`, `skip_ribocode`, and the opt-in `run_ribotricer`, alignment
outputs, GTF compatibility, and P-site/protocol settings.

If translational efficiency fails, check that the samplesheet has matched `rnaseq` and `riboseq`
rows, that the contrast file columns exist in the samplesheet, and that optional batch or pair
columns are correctly named.


## Requested release

Read `07_version_update.md` for the pinned release's parameter changes, additional routes,
output locations and QC caveats before adapting a previous analysis.

For Bowtie2 filtering failures confirm the FASTA paths in ribo_database_manifest; do not supply a SortMeRNA index. For unexpected TE counts check te_quantification_method and skip_plastid before changing statistics.
