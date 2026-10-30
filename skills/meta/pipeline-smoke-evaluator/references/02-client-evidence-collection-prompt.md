# Client Evidence Collection Prompt

Use this prompt in the same client-agent session immediately after one smoke run has finished.

It is written for a client agent such as Claude Code.

## Purpose

The prompt tells the client agent to save the minimal evidence bundle required by
`pipeline-smoke-evaluator`.

It assumes:

- the smoke task has already been executed in the current session
- the client agent still has access to its own recent tool calls and outputs
- the hidden evaluation spec exists under `tests/pipeline_support/<pipeline>/smoke.yaml`

## Ready-to-paste prompt

```text
The smoke run is already finished in this same session.
Do not rerun the pipeline.
Do not regenerate the task.
Only collect and save the minimal evaluation evidence bundle for the completed run.

Use the current session history and the completed run artifacts to create an `eval_bundle` directory.

Inputs:
- case directory: `tests/pipeline_support/<pipeline>`
- hidden evaluation spec: `tests/pipeline_support/<pipeline>/smoke.yaml`
- task prompt: `tests/pipeline_support/<pipeline>/smoke.task.md`
- target evidence directory: `<eval_bundle_dir>`

Required outputs to save:
1. `task_brief.md`
   - copy the exact task prompt used for this run from `tests/pipeline_support/<pipeline>/smoke.task.md`
2. `smoke.yaml`
   - copy the hidden evaluation spec into the evidence directory for later offline evaluation
3. `run_request.json`
   - save the actual completed `nextflow_run(...)` request for the real run
   - include only the final real launch, not exploratory drafts
   - preserve these fields when available:
     - `pipeline`
     - `project`
     - `run_name`
     - `params`
4. `run_result.json`
   - save the final completed run result for that launch
   - include:
     - `run_id`
     - `project_id`
     - `status`
     - `exit_code` if available
     - `run_layout` if available
     - one compact `artifact_summary` block if available
5. `output_checks.json`
   - read `smoke.yaml.assertions.artifacts.required_paths`
   - check whether each required path exists under the completed run outputs
   - save:
     - `required_paths`
     - `verified_paths`
     - `missing_paths`

Rules:
- Do not save guesses.
- If one file cannot be reconstructed from the current session, create the file anyway and set:
  - `"available": false`
  - `"reason": "<short concrete reason>"`
- Use the completed run from this session only.
- If there were multiple real runs in this session, use the final completed run that produced the current output directory.
- Keep all JSON files compact and machine-readable.

At the end, report:
- the absolute path of the saved `eval_bundle` directory
- which required evidence files were successfully written
- which files were incomplete and why
```

## Notes

- Replace `<pipeline>` and `<eval_bundle_dir>` before sending the prompt.
- If the client can also save the original user prompt, add an optional `prompt.txt`.
- If the run failed and the client already inspected logs, it may also save `failure_logs.txt`, but
  that file is not required by the simplified evaluator.
