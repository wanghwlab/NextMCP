---
name: pipeline-test-converter
description: >-
  Use whenever the user wants to convert a repository-local or nextmcp-visible
  pipeline test setup into a hidden evaluation spec for a lightweight test run.
  In this repository, that spec is still called a `smoke contract`. Use it for
  batch evaluation, system testing, or expert-skill validation. Trigger after a
  pipeline has been classified into `profile-only`,
  `profile-plus-tests-config`, `requires-local-cache`, or
  `unsuitable-for-generic-smoke`, or when the user directly asks to turn
  `nextflow.config`, `conf/test*.config`, `tests/nextflow.config`, and
  `tests/*.nf.test` into a minimal runnable smoke task with assertions and
  agent-facing prompt material.
compatibility: >-
  Works with either a repository-local pipeline checkout or a nextmcp-visible
  pipeline whose own test materials can be read. Requires the selected setup to
  have already been classified, or enough access to `nextflow.config`,
  `conf/test*.config`, `tests/nextflow.config`, `tests/*.nf.test`,
  `tests/*.snap`, and `.nftignore` to classify and convert it safely.
metadata:
  skill-class: meta
  tool-surface: nextmcp
  tool-surface-version: "2026-03-27"
  generated-from: repository pipeline test-material conversion rules
---

# Pipeline Test Converter

## Scope

Use this skill to convert one lightweight test setup from the original pipeline repository into a
standard hidden evaluation spec for a lightweight test run.

This skill is the conversion layer. It assumes the test setup has already been classified, or that
the needed evidence can be read quickly from the pipeline files.

## When to use this skill

Use this skill after the source route is known and the goal is to turn one upstream test setup into
one hidden nextmcp evaluation contract with launch details, runtime inputs, assertions, and a short
client-visible brief.

## What this skill does not handle

- deciding repository-wide batch strategy across many pipelines
- downloading or mirroring remote files by itself when localization has not been planned
- replacing a pipeline-specific expert skill for normal user support
- exposing internal conversion mechanics in the main client brief

## Authoritative assets

- `assets/contract-schema.yaml`

## References to read next

- `references/01-conversion-workflow.md`
- `references/02-mode-handlers.md`
- `references/03-assertion-derivation.md`

## Operating rules

### Output

Return one hidden evaluation spec with these sections:

- `mode`
- `source_route`
- `runtime_inputs`
- `localization_plan`
- `launch_plan`
- `assertions`
- `prompt_brief`
- `blockers`

Use the schema in `assets/contract-schema.yaml`.

### Input sources

Build the contract from these files in order:

1. `nextflow.config`
2. `conf/test*.config`
3. `tests/nextflow.config` when the mode requires it
4. `tests/*.nf.test`
5. `tests/*.snap` and `.nftignore` for stable assertions

Do not use repository-local support layers such as `tests/pipeline_support/` unless the user
explicitly asks to convert those materials instead of the pipeline repository's own test
materials.

### Conversion modes

### profile-only

Use runtime config as the main source of truth.

Output should include:

- canonical test profile such as `test` or one `test_*`
- direct params from `conf/test*.config`
- process-level notes that matter for equivalence
- localization plan for remote URLs or `projectDir/tests/...` inputs
- minimal launch plan using `nextflow_run(prepare=true)` first

When localization produced task-local downloads or rewritten manifests, prefer those localized
paths in `runtime_inputs`, `localization_plan`, and `launch_plan`. Do not default to external
shared mirror roots unless the task explicitly depends on them.

### profile-plus-tests-config

Use runtime config as the base setup, then merge the required shared values from
`tests/nextflow.config`.

Only pull fields that materially affect the test setup, for example:

- shared base paths such as `pipelines_testdata_base_path`
- test-wide input defaults
- resource limits or auth assumptions that are required to interpret the setup

Do not blindly copy all nf-test harness settings into the final evaluation spec.

### requires-local-cache

Treat the current repository test setup as dependent on prelocalized server-local files.

Output should include:

- cache-root assumptions
- exact local files or directories that must exist
- whether the setup can be generalized later by replacing local cache paths with localized remote
  sources

If the local cache manifest is missing, return a blocker instead of pretending the setup is ready.

### unsuitable-for-generic-smoke

Do not force a runnable contract.

Output should explain why the test setup should be skipped from the standard batch and what adapter
would be needed to recover it.

### Assertions

Keep assertions small and stable.

Prefer this order:

1. process succeeds
2. key output directories or files exist
3. one or two content checks for anchor files when the content is stable

Use `.snap` and `.nftignore` as evidence sources, not as a requirement to reproduce the full
nf-test snapshot.

### Prompt brief rules

Treat `prompt_brief` as the future client-visible `smoke.task.md`.

Keep it limited to:

- the task goal
- available server-local inputs and output locations
- key route constraints only when they are directly supported by the source materials
- source-backed resource-cap summaries when the selected test config defines concrete limits

Keep these out of the main brief:

- internal source file names such as `conf/test.config`, `tests/default.nf.test`, `.snap`, or
  `tests/pipeline_support/...`
- framing such as test, validation run, or production analysis unless the user explicitly asked
- launch mechanics such as `nextflow_run(prepare=true)`, `config_files`, override config paths,
  raw Groovy config blocks, or server-side preparation steps
- author inferences that are not directly supported by the selected source materials

When the selected source materials define concrete resource caps, restate them once in plain
language in `prompt_brief`, then keep the implementation channel in `launch_plan`,
`localization_plan`, or secondary agent notes.

Keep execution mechanics and strict param mapping in `launch_plan`, `localization_plan`, or
secondary agent notes, not in `prompt_brief`.

### Integration with other skills

- Use `pipeline-test-mode-classifier` first when the mode is still unknown.
- Reuse the rules in `pipeline-test-config-localizer` when the contract needs remote input
  localization, manifest rewriting, or server-local path mapping.
- Do not replace pipeline-specific expert skills. This skill only produces smoke-eval contracts.

### Workflow

1. Confirm or infer the mode.
2. Choose the canonical lightweight test setup from the pipeline repository.
3. Extract runtime inputs from the allowed source files for that mode.
4. Build a localization plan.
5. Build a launch plan.
6. Derive a minimal stable assertion set.
7. Render a short client-visible prompt brief that states the task in normal user language without
   exposing internal source files or execution mechanics, but keep concrete source-backed resource
   caps visible as route constraints.

## Fast-start workflow

1. Confirm the mode and chosen source route.
2. Extract runtime inputs only from the allowed source files for that mode.
3. Build localization and launch sections separately from the client brief.
4. Keep assertions short and stable.
5. Render `prompt_brief` as a plain task prompt with only source-backed route constraints and any
   concrete source-backed resource caps.
