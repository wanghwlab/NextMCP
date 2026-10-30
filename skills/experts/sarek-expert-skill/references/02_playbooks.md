# Playbooks

Start with `assets/playbooks.yaml`; this file explains the main routes.

For a standard run, confirm `project`, `input`, `outdir`, and `step`. Use
`nextflow_run(prepare=true)` when the samplesheet, target outdir, or run layout is still uncertain,
then launch with `nextflow_run(pipeline="sarek", project=..., params=...)`. After launch, read
`run_get(include=["progress","artifact_summary","diagnosis","next_actions"])`.

For WES or targeted data, set `wes: true` and provide `intervals`. Do not disable intervals by
default. Mutect2 somatic planning is especially sensitive to interval choices.

For tumor-normal analysis, check samplesheet metadata before changing callers. Sarek pairs samples
by shared `patient`, distinct `sample`, and `status` values where `0` is normal and `1` is tumor.
The tools list chooses the caller families: `mutect2`, `strelka`, `manta`, `tiddit`, `ascat`,
`cnvkit`, `controlfreec`, `msisensor2`, `msisensorpro`, and related callers.

For annotation-only runs, use `step: annotate` and a VCF samplesheet. Pick `tools` from `vep`,
`snpeff`, `merge`, `bcfann`, and `snpsift`. Confirm caches and plugin database paths before
launching.

For historical reuse, search with `run_list(project=..., pipeline="sarek",
artifact_path_contains=...)`, inspect `run_get(include=["artifact_summary"])`, then use
`run_artifacts(...)`. Treat `artifacts.json` and `pipeline_fingerprint` as historical facts and
confirm compatibility through `pipeline_info/params.json` before recommending reuse.
