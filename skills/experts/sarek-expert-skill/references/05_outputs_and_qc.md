# Outputs And QC

Start with `run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`. Then use
`run_artifacts(...)` for the relevant sections. Use `fs_read` only after nextmcp returns a concrete
path.

The first review targets are `pipeline_info/` and `multiqc/multiqc_report.html`. `pipeline_info`
contains params, software versions, execution reports, trace, timeline, DAG, and provenance files.
MultiQC summarizes FastQC, FastP, mosdepth, samtools, bcftools, VCFtools, SnpEff, VEP, and other
reports when those tools ran.

Preprocessing outputs live under `preprocessing/`, including `fastp`, `umi`, `bbsplit`, `mapped`,
`markduplicates`, `sentieon_dedup`, `recal_table`, `recalibrated`, `parabricks`, and `csv`
subdirectories depending on route and save switches.

Variant outputs live under `variant_calling/`, with caller-specific subdirectories such as
`haplotypecaller`, `mutect2`, `strelka`, `manta`, `tiddit`, `ascat`, `cnvkit`, `controlfreec`,
`msisensor2`, `msisensor`, `filtered`, `normalized`, `consensus`, and `concat`.

Annotation outputs live under `annotation/`; tool reports for SnpEff and VEP live under
`reports/SnpEff/` and `reports/EnsemblVEP/`.

For reuse, search with fragments like `pipeline_info/params.json`, `multiqc_report.html`,
`variant_calling/mutect2`, or `annotation`. Confirm compatibility through `pipeline_info/params.json`
or equivalent metadata before presenting reuse as safe.
