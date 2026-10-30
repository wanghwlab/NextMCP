# Max job request options

The runtime agent may see source schema names in the `Max job request options`
section, but resource caps for this nf-core pipeline should be rendered in config
scope, not passed as ordinary pipeline params.

Use `process { resourceLimits = [...] }` in a server-local config file and pass that
file with `nextflow_run(config_files=[...])`. Do not invent `params.max_cpus`,
`params.max_memory`, `params.max_time`, or `process.maxCpus`.

- Exact source: `assets/schema-groups/max_job_request_options.yaml`
- Discovery index: `assets/schema-index.yaml`

## Route-shaping

No route-shaping parameters were classified into this group.

## Lookup-only

- `max_cpus`
- `max_memory`
- `max_time`

These names are preserved for source-backed lookup. They are not the rendered
runtime shape for resource caps in this skill.

## Non-runtime

No non-runtime or authoring-only parameters were classified into this group.
