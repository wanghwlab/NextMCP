# Outputs And QC

Start post-run review with `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`. Use `run_artifacts(...)` before reading individual files. Use `fs_read()` only after a concrete file path is known.

## Review Order

1. `summary_report/summary_report.html` for the human-readable analysis overview.
2. `multiqc/multiqc_report.html` for aggregate QC and software summaries.
3. `overall_summary.tsv` for read retention through major stages.
4. `cutadapt/cutadapt_summary.tsv` when primer trimming ran.
5. `dada2/ASV_table.tsv`, `dada2/ASV_seqs.fasta`, and `dada2/DADA2_stats.tsv` for core ASV outputs.
6. `dada2/ASV_tax.*.tsv`, `sintax/`, `kraken2/`, `qiime2/taxonomy/`, or `pplace/` for taxonomy outputs depending on route.
7. `qiime2/abundance_tables/feature-table.tsv` and `qiime2/rel_abundance_tables/rel-table-ASV.tsv` for downstream abundance tables.
8. `qiime2/barplot/`, `qiime2/alpha-rarefaction/`, and `qiime2/diversity/` for metadata-driven visual and diversity outputs.
9. `qiime2/ancom/`, `qiime2/ancombc/`, `PICRUSt2/`, `SBDI/`, `phyloseq/`, and `treesummarizedexperiment/` when requested.
10. `pipeline_info/params.json` and `pipeline_info/software_versions.yml` for provenance and reuse checks.

## QC Signals

Use `assets/qc-rules.yaml` for the exact checks. Key checks are input-route consistency, primer trimming retention, DADA2 read retention, DADA2 error-model convergence, taxonomy database suitability, metadata-driven QIIME2 output presence, and correct resource-cap placement.

For historical reuse, search by known artifact fragments and confirm compatibility with `pipeline_info/params.json`. Do not guess old output directories as the default safe path.
