# Outputs And QC

Use `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])` before raw logs
or file reads. Then use `run_artifacts` for the relevant section and `fs_read` only for explicit
files.

First review `multiqc/multiqc_report.html`, `pipeline_info/`, and `pipeline_info/params.json` when
available. MultiQC is the main summary for FastQC, SAMtools, featureCounts, software versions, and
workflow metadata. `pipeline_info` contains execution reports, trace files, the validated
samplesheet, and software versions.

For demultiplexing, inspect `qcat/fastq/<barcode*>.fastq.gz` and `qcat/fastq/none.fastq.gz`. If
most reads are unassigned, recheck `barcode_kit`, `barcode_both_ends`, `trim_barcodes`,
`qcat_detect_middle`, and `qcat_min_score`.

For raw read QC, inspect `nanoplot/fastq/` and `fastqc/`. Read quality and length distributions
should match the protocol before interpreting alignment, variants, or RNA outputs.

For alignment, inspect `<ALIGNER>/<SAMPLE>.sorted.bam`, BAM indexes, and
`<ALIGNER>/samtools_stats/`. Use the selected aligner name, usually `minimap2` unless the user
requested `graphmap2`.

For coverage tracks, inspect `<ALIGNER>/bigwig/` and `<ALIGNER>/bigbed/`. bigBed is relevant for
RNA protocols; `skip_bigwig` and `skip_bigbed` control these outputs.

For DNA variants, inspect `variant_calling/medaka_variant/`, `variant_calling/deepvariant/`,
`variant_calling/margin_pepper_deepvariant/`, `variant_calling/sniffles/`, or
`variant_calling/cutesv/` according to the selected callers and skip toggles.

For RNA quantification, inspect `bambu/` or `stringtie2/`. bambu emits `extended_annotations.gtf`,
`counts_gene.txt`, and `counts_transcript.txt`. StringTie2 emits per-sample GTFs,
`stringtie.merged.gtf`, and featureCounts gene/transcript count tables.

For differential analysis, inspect `<QUANTIFICATION_METHOD>/deseq2/deseq2.results.txt` and
`<QUANTIFICATION_METHOD>/dexseq/dexseq.results.txt`.

For direct RNA modification analysis, inspect
`rna_modifications/xpore/diffmod/diffmod_outputs/diffmod.table` and
`rna_modifications/m6anet/inference/<sample_name>/data.result.csv.gz`.

For fusion analysis, inspect `jaffal/jaffa_results.csv` and `jaffal/jaffa_results.fasta`.

For historical reuse, search with `run_list(..., artifact_path_contains=...)` using exact fragments
from `assets/artifact-contracts.yaml`, then confirm compatibility through `pipeline_info/params.json`
or equivalent run metadata.
