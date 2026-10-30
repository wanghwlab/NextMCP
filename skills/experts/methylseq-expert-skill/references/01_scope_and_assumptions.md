# Scope and Assumptions

This package was generated from a repository-local inspect-equivalent authoring bundle built from `nf_pipeline/methylseq`. The authoring bundle used the same top-level source shape as `nextflow_inspect_pipeline(detail="materials")`: schema, documents, and source files. One targeted nested workflow file, `workflows/methylseq/main.nf`, was read to confirm route behavior.

The pipeline is nf-core/methylseq 4.2.0. It analyzes short-read methylation data with Bismark, Bismark-HISAT2, BWA-Meth, and BWA-MEM/TAPS routes.

Supported runtime routes:

- `bismark_default`: default bisulfite route with Bismark and Bowtie2.
- `bismark_hisat_slamseq`: Bismark with HISAT2, including splice-aware and SLAM-seq planning.
- `bwameth_methyldackel`: BWA-Meth with MethylDackel extraction.
- `gpu_bwameth`: BWA-Meth with a GPU runtime profile when the server supports it.
- `taps_bwamem_rastair`: BWA-MEM or TAPS route with Rastair outputs.
- `targeted_sequencing`: target BED filtering and optional Picard CollectHsMetrics.
- `optional_qc_outputs`: Qualimap, preseq, saved intermediates, unmapped reads, or saved references.

All runtime paths are server-local nextmcp paths. The client machine path is not a valid substitute for a server path. Use `fs_list(mode="manifest")` only to confirm a concrete path when needed.

Do not use `nextflow_inspect_pipeline` during normal runtime planning. Use packaged assets first, then nextmcp runtime tools.
