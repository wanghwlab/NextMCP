---
name: pipeline-smoke-evaluator
description: >-
  Evaluate one completed nextmcp smoke test against its hidden evaluation spec
  using a small saved evidence bundle. In this repository, that spec is stored
  in `smoke.yaml` and is still referred to as a `smoke contract` in some places.
  Use when a pipeline smoke run has already finished, you have a hidden
  `tests/pipeline_support/*/smoke.yaml` file plus a saved run request/result
  bundle, and you want a compact verdict on three simple checks: whether the
  task was translated into the intended run, whether the run completed, and
  whether the required outputs were present. Do not use this skill to generate
  these evaluation specs or to run the pipeline itself.
compatibility: >-
  Requires a completed run evidence bundle plus the corresponding hidden
  contract files under `tests/pipeline_support/<pipeline>/`, especially
  `smoke.yaml`. The evaluator only needs read access to those saved files.
metadata:
  skill-class: meta
  tool-surface: nextmcp
  tool-surface-version: "2026-03-27"
  generated-from: repository smoke-run evidence evaluation rules
---

# Pipeline Smoke Evaluator

## Scope

Use this skill after one smoke run is complete.

It reads the hidden evaluation spec from `tests/pipeline_support/<pipeline>/` and a saved evidence
bundle from the completed client run, then returns one compact verdict.

## When to use this skill

Use this skill when the run is already finished and the user wants a short verdict on whether the
saved request, result, and output evidence match the hidden contract.

## What this skill does not handle

- generating `smoke.yaml` or `smoke.task.md`
- rerunning the pipeline
- rebuilding missing evidence from scratch
- expanding the verdict into a larger internal review unless the user explicitly asks

## Authoritative assets

- `tests/pipeline_support/<pipeline>/smoke.yaml`
- `tests/pipeline_support/<pipeline>/smoke.task.md`
- `references/01-evidence-bundle.md`
- `references/02-client-evidence-collection-prompt.md`

## References to read next

- `references/01-evidence-bundle.md`
- `references/02-client-evidence-collection-prompt.md`

## Operating rules

### Required inputs

Provide either:

1. `case_dir`
   Example: `tests/pipeline_support/scrnaseq`

2. `eval_bundle_dir`
   A directory with the minimal saved evidence bundle from the completed run

Or explicit paths to:

- `smoke.yaml`
- `smoke.task.md`
- `run_request.json`
- `run_result.json`
- `output_checks.json`

Read [references/01-evidence-bundle.md](references/01-evidence-bundle.md) for the expected bundle
shape.

### What to evaluate

Return only three simple checks:

1. `task_translated_correctly`
2. `run_completed`
3. `required_outputs_present`

Then return one overall result:

- `pass`
- `fail`
- `insufficient_evidence`

### Default workflow

1. Read `smoke.yaml` to get:
   - `pipeline`
   - `case_id`
   - `launch`
   - `assertions.run.final_status`
   - `assertions.artifacts.required_paths`
2. Read `run_request.json` and compare only the key launch fields:
   - `pipeline`
   - `project`
   - optional `run_name`
   - required `params`
3. Read `run_result.json` and check whether the terminal status matches the evaluation spec.
4. Read `output_checks.json` and check whether every required path is marked present.
5. Return one compact verdict with short notes.

### Scoring rules

### 1. `task_translated_correctly`

Pass when the completed run request is semantically aligned with `smoke.yaml.launch`.

Check only the fields that define the lightweight test setup:

- `pipeline`
- `project`
- optional `run_name`
- required `params`

Do not fail the case for harmless extra fields that do not change the setup.

### 2. `run_completed`

Pass when `run_result.json` shows the terminal status required by
`smoke.yaml.assertions.run.final_status`.

If the bundle includes `run_id`, `project_id`, `run_layout`, or `exit_code`, keep them in notes,
but the primary check is the final status.

### 3. `required_outputs_present`

Pass when every path in `smoke.yaml.assertions.artifacts.required_paths` is present in
`output_checks.json`.

Do not require full snapshot equality.
Only require the minimal anchor outputs listed in the contract.

### Missing evidence rules

Do not guess.

If any required evidence file is missing or unreadable:

- report which file is missing
- set the affected metric to `unknown`
- set `overall_result = insufficient_evidence`

Examples:

- missing `run_request.json` -> cannot judge `task_translated_correctly`
- missing `run_result.json` -> cannot judge `run_completed`
- missing `output_checks.json` -> cannot judge `required_outputs_present`

### Output format

Return one compact YAML block like this:

```yaml
pipeline: scrnaseq
case_id: smoke
task_translated_correctly: yes
run_completed: yes
required_outputs_present: yes
overall_result: pass
notes: []
missing_evidence: []
```

If evidence is incomplete:

```yaml
pipeline: scrnaseq
case_id: smoke
task_translated_correctly: unknown
run_completed: yes
required_outputs_present: unknown
overall_result: insufficient_evidence
notes:
  - output checks were not saved
missing_evidence:
  - output_checks.json
```

### Boundaries

- Do not create or modify `smoke.yaml`.
- Do not rerun the pipeline unless the user explicitly asks for that.
- Do not try to reconstruct the full MCP trace from outputs alone.
- Do not expand this into the older five-metric internal evaluation unless the user explicitly asks.
- Keep the verdict short and concrete.

## Fast-start workflow

1. Read `smoke.yaml` first so the required launch fields and required outputs are fixed.
2. Check the saved request, result, and output evidence against only those required fields.
3. Mark missing evidence as `unknown` instead of guessing.
4. Return one short YAML verdict.
