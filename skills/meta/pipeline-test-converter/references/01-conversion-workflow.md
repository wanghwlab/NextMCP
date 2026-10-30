# Conversion Workflow

## Goal

Turn one lightweight test setup from the pipeline repository into one standard hidden evaluation
spec for a lightweight test run.

## Steps

1. Confirm the mode.
   Use the classifier output when available. If it is missing, infer the mode quickly from the
   same evidence order used by the classifier.
2. Choose the canonical lightweight test setup.
   Prefer `test`, else one small `test_*` profile that still looks like a normal run.
3. Extract runtime inputs.
   Read `conf/test*.config` first. Pull from `tests/nextflow.config` only when the mode requires
   it.
4. Build the localization plan.
   Separate:
   - remote URLs
   - repo-local `projectDir/tests/...` files
   - already-local cache paths
5. Build the launch plan.
   Prefer:
   - `nextflow_run(prepare=true)`
   - then real `nextflow_run(...)`
6. Derive assertions.
   Use the smallest stable set that still proves the setup works.
7. Render the prompt brief.
   Keep it client-visible and natural.
   Include the task goal, available inputs, and only directly sourced route constraints.
   Do not mention internal source file names, `nextflow_run(prepare=true)`, `config_files`,
   override config paths, raw Groovy config blocks, or other execution mechanics.
   If the selected source route defines concrete resource caps, restate them once in plain
   language in the brief.

## Output style

Keep the final evaluation spec compact and operational. Avoid turning it into a long narrative.
