# Prompt Rendering

The final deliverable is a natural-language instruction for the runtime agent,
not a raw config dump.

## Rendering rules

- Speak as if the user does not know the upstream param names.
- Name each local file by purpose first, path second.
- Mention that the files already live on the nextmcp server filesystem.
- Prefer paths from the current localized bundle in the brief and agent note.
- Keep config syntax, Groovy blocks, and direct URI lists out of the main brief.
- Keep launch mechanics such as `nextflow_run(prepare=true)`, `config_files`,
  override config paths, and raw Groovy config blocks out of the main brief.
- When the source-backed route includes concrete resource caps, summarize them once in plain
  language in the main brief.
- Do not mention internal source file names such as `conf/test.config`,
  `tests/default.nf.test`, `.snap`, or `tests/pipeline_support/...` in the main
  brief.
- Do not frame the task as a test, validation run, or production analysis
  unless the user explicitly asked for that wording.
- Keep only route constraints that are directly supported by the source
  materials.
- Put any strict param mapping or config-scoped execution detail into a
  secondary agent note.

## What to translate into prose

Translate these into plain language:

- dataset role: input samplesheet, contrasts table, rRNA manifest, genome FASTA, annotation GTF
- task goal
- meaningful behavior switches such as skipping a pipeline branch
- special validation flags that materially affect the run

Do not translate blindly:

- config-only mechanics that the runtime agent cannot express as a normal
  pipeline param
- decorative comments
- profile labels that do not matter after inputs and run intent have been restated
- author inferences that are not directly supported by the selected source
  materials

When the upstream test route relies on config-scoped resource caps such as
`max_cpus`, `max_memory`, and `max_time`, keep them out of the main params list.
Still mention the cap values once in plain language in the main brief, and keep
the implementation channel in a secondary agent note or launch plan.

## Example brief for `riboseq/conf/test.config`

Use wording in this shape:

```markdown
# Task
Run the `riboseq` pipeline on the prepared local dataset that is already
available on this server.

## Available inputs
- Samplesheet: `<server_input_root>/testdata/riboseq/test/.../samplesheet_local.csv`
- Contrasts table: `<server_input_root>/testdata/riboseq/test/.../contrasts.csv`
- rRNA manifest: `<server_input_root>/testdata/riboseq/test/.../rrna-db_local.txt`
- Reference genome: `<server_input_root>/testdata/riboseq/test/.../Homo_sapiens.GRCh38.dna.chromosome.20.fa.gz`
- Gene annotation: `<server_input_root>/testdata/riboseq/test/.../Homo_sapiens.GRCh38.111_chr20.gtf`

## Route constraints
- Keep the minimum trimmed-read threshold at 1000.
- Skip the Ribotricer branch.
- Keep the upstream test resource caps at 4 CPUs, 15.GB memory, and 1.h runtime.
```

## Secondary agent note

Keep a short mapping note outside the main user-facing brief, for example:

- samplesheet.csv -> `samplesheet_local.csv`
- rrna-db.txt -> `rrna-db_local.txt`
- preferred mirror missing -> task-local download under the current `localized_root`
- `input` -> localized `samplesheet_local.csv`
- `contrasts` -> localized `contrasts.csv`
- `ribo_database_manifest` -> localized `rrna-db_local.txt`
- `fasta` -> localized chromosome 20 FASTA
- `gtf` -> localized GTF
- `min_trimmed_reads` -> `1000`
- `skip_ribotricer` -> `true`
- `extra_fqlint_args` -> original string preserved exactly
- `nextflow_run(prepare=true)` -> launch sequence detail kept out of the main brief
- resource caps -> summarize once in the main brief and keep the small server-local override
  config detail in `config_files`
