# Scope And Assumptions

This package was generated from a repository-local inspect-equivalent authoring bundle rooted at
`https://github.com/nf-core/riboseq/tree/2.0.0`. The bundle used `nextflow_schema.json`,
`README.md`, top-level docs, `main.nf`, `nextflow.config`, and top-level entry scripts.

The skill covers `nf-core/riboseq` 2.0.0 runs through nextmcp. Use it for standard Ribo-seq or
TI-seq analyses, matched RNA-seq/Ribo-seq translational efficiency analysis, UMI-aware runs,
rRNA filtering, BBSplit contaminant screening, reference index build or reuse, extended ORF analysis, output review, historical reuse, and troubleshooting.

All runtime paths are server-local. The `project` identifier, `params.input`, reference paths,
`params.outdir`, and relative path-like values in `params` or `config_files` are resolved on the
nextmcp server filesystem. Do not pass client-local paths. When a concrete path is unknown, use
server-scoped placeholders such as `<server_input_root>/samplesheet.csv`.

The main samplesheet must begin with `sample,fastq_1,fastq_2,strandedness,type`. The `type` column
may contain `riboseq`, `tiseq`, or `rnaseq`. Translational efficiency requires both Ribo-seq and
RNA-seq samples plus a contrasts file.