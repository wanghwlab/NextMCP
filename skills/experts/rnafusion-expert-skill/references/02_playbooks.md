# Playbooks

Use `assets/playbooks.yaml` as the exact route list. This reference gives the decision logic in
plain language.

## Full Detection

Use `standard_all_tools_run` when the user wants a full rnafusion analysis. Confirm the project id,
the server-local samplesheet, `genomes_base`, and the output directory. Use the
`full_detection_all_tools` preset, then prepare or launch with:

```text
nextflow_run(pipeline="rnafusion", project=..., params={
  "tools": "all",
  "input": "<server_input_root>/samplesheet.csv",
  "genomes_base": "<server_reference_root>/rnafusion",
  "outdir": "<server_output_root>/rnafusion"
})
```

Omit `profile` unless the user asks for a specific runtime or the server default is unsuitable.

## Selected Tools

Use `selected_tools_run` when the user asks for a subset such as `arriba,starfusion,fusionreport`.
Check that the selected tools are allowed by the schema. Include `fusionreport` when downstream
FusionInspector should use caller results. Include `fastp` when trimming is requested. Do not use
Conda or Mamba with `ctatsplicing`.

## Reference Building

Use `build_references` before analysis when rnafusion references are missing or stale. Set
`references_only=true`, choose `tools`, and set both `genomes_base` and `outdir` to server-local
reference paths. Building references can take a long time. If COSMIC is unavailable, use
`no_cosmic=true`. If QIAGEN credentials are used, set `qiagen=true` only after the user confirms
that route.

## FusionInspector Only

Use `fusioninspector_only` when the user already has a fusion list. Confirm the
`fusioninspector_fusions` file exists on the server and contains `GENE1--GENE2` rows. Use
`tools=fusioninspector`. The packaged preset also sets `skip_qc=true`, `skip_vis=true`, and
`skip_vcf=true` for the minimal route.

## FusionCatcher Trimming

Use `trimming_for_fusioncatcher` when FusionCatcher is selected and reads are longer than the
recommended 100 bp. Add `fastp` and set `trim_tail_fusioncatcher` to the number of 3-prime bases
to remove. Review the extra `fastp` reports for FusionCatcher-specific reads.

## Post-Run Review

Start with:

```text
run_get(include=["progress","artifact_summary","diagnosis","next_actions"])
```

Then use `run_artifacts(...)` for sections such as `fusionreport`, `fusioninspector`, `vcf`,
`multiqc`, or `pipeline_info`. Use `fs_read` only after a concrete file path is known.
