# Evidence Bundle

This skill expects a small saved bundle from one completed smoke run.

## Required files

### `run_request.json`

Minimum useful fields:

```json
{
  "pipeline": "scrnaseq",
  "project": "scrnaseq-smoke",
  "run_name": "smoke",
  "params": {
    "input": "...",
    "outdir": "...",
    "fasta": "...",
    "gtf": "..."
  }
}
```

### `run_result.json`

Minimum useful fields:

```json
{
  "run_id": "run_20260328_123456",
  "project_id": "scrnaseq-smoke",
  "status": "succeeded",
  "exit_code": 0,
  "run_layout": {
    "run_root": "...",
    "job_dir": "...",
    "results_dir": "..."
  }
}
```

If available, include one compact `artifact_summary` block too.

### `output_checks.json`

This file should already compare the real output tree against
`smoke.yaml.assertions.artifacts.required_paths`.

Minimum useful shape:

```json
{
  "required_paths": [
    "multiqc",
    "star/mtx_conversions/combined_filtered_matrix.h5ad"
  ],
  "verified_paths": [
    "multiqc",
    "star/mtx_conversions/combined_filtered_matrix.h5ad"
  ],
  "missing_paths": []
}
```

## Optional files

- `task_brief.md`
- `prompt.txt`
- `artifact_summary.json`
- `failure_logs.txt`

These help review, but the simplified verdict does not require them.

## Minimal verdict logic

Use this bundle to answer only three questions:

1. Did the completed run request match the hidden evaluation spec?
2. Did the run reach the required final status?
3. Did the required output paths exist?

If one of the required files is missing, return `insufficient_evidence` instead of guessing.
