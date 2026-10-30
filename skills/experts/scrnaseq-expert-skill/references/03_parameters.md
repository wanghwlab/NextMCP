# Parameters

Use `assets/param-presets.yaml` for the compact launch layer. Use `assets/schema-index.yaml` and one grouped schema file when exact type, default, enum, or path format matters.

## Required Inputs

- `input`: server-local CSV samplesheet.
- `outdir`: server-local published result directory.
- `protocol`: concrete chemistry for Simpleaf, STARsolo, and Kallisto/BUS. `auto` is only valid for Cell Ranger routes in the source workflow.
- Reference inputs: use `genome`, aligner-specific prebuilt index, or FASTA/GTF plus route-specific files.

## Route-Shaping Parameters

- `aligner`: one of `simpleaf`, `star`, `kallisto`, `cellranger`, `cellrangerarc`, or `cellrangermulti`.
- `protocol`: chemistry or custom protocol string.
- `save_reference`: publish generated Simpleaf, STAR, or Kallisto references for later reuse.
- `save_align_intermeds`: publish STAR or Cell Ranger intermediate alignment files.
- `skip_cellbender`: disables CellBender filtering when true.
- `star_feature`: `Gene`, `GeneFull`, or `Gene Velocyto`.
- `kb_workflow`: `standard`, `lamanno`, or `nac`.

## Channel Boundaries

Put ordinary pipeline-facing options in `nextflow_run(params=...)`: samplesheets, references, indices, route selectors, skip flags, and output directory.

Put resource caps in a small server-local config and pass it with `nextflow_run(config_files=[...])`:

```nextflow
process {
  resourceLimits = [
    cpus: 16,
    memory: '64.GB',
    time: '24.h'
  ]
}
```

Do not put `max_cpus`, `max_memory`, or `max_time` under `params` for nextmcp launches. Keep `project` as a top-level `nextflow_run` argument. Use `from_run_id` for public restart planning after checking `run_get(detail="full")`.

## Exact Lookup

Open `assets/schema-index.yaml`, find the parameter group, then open the matching `assets/schema-groups/*.yaml` file. For example, `aligner` and `protocol` are in `mandatory_arguments`, Cell Ranger Multi fields are in `cellranger_multi_options`, and `skip_cellbender` is in `skip_tools`.
