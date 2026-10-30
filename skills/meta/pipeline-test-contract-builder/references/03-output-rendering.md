# Output Rendering

## classification

Keep this short:

- one primary mode
- flat modifier list
- 3 to 6 evidence bullets
- one next action

## localization

Use one of these forms:

### not needed

```text
not_needed
```

### completed

Include:

- remote sources found
- local rewrite targets
- server-local root
- manifest rewrite notes

### blocked

Include:

- missing fetch surface
- missing writable root
- missing cache root
- unsupported URI scheme

## contract

Include the full contract only when it is usable enough for evaluation.

Minimum sections:

- `mode`
- `source_route`
- `runtime_inputs`
- `localization_plan`
- `launch_plan`
- `assertions`
- `prompt_brief`
- `blockers`

## final_status

Use:

- `ready` when the contract is usable
- `blocked` when prerequisites are missing
- `skip` when the route should stay out of the standard batch
