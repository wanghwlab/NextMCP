# Scope And Assumptions

Use this skill for `nf-core/sarek` runs through nextmcp. It covers WGS, WES, targeted sequencing,
germline and somatic variant calling, tumor-normal pairs, UMI handling, BBSplit contamination
removal, Sentieon routes, CNV/SV/MSI tools, SnpEff/VEP/SnpSift/bcftools annotation, output review,
historical reuse, and exact schema lookup.

All runtime paths resolve on the nextmcp server filesystem. The client machine path is not enough.
Use paths returned by nextmcp tools or paths the user has confirmed exist on the server. When
drafting examples, use placeholders such as `<server_input_root>/sarek_samplesheet.csv` and
`<server_reference_root>/...`.

The main runtime entry is the pipeline id `sarek`. The current source manifest version is 3.8.1.
The pipeline default `step` is `mapping`; valid step values are `mapping`, `markduplicates`,
`prepare_recalibration`, `recalibrate`, `variant_calling`, and `annotate`.

Sentieon planning is supported, but license setup is outside this skill. The runtime agent should
only proceed when the user confirms the server has the Nextflow secret
`SENTIEON_LICENSE_BASE64`. Do not ask for or store the license value.

Resource changes belong in `config_files`, not `params`. Sarek source configs use process-level
settings and the test configs show `process.resourceLimits`; use that exact form for caps.
