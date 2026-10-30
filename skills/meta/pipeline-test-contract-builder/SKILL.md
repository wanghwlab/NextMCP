---
name: pipeline-test-contract-builder
description: >-
  Use whenever the user wants a one-shot workflow that classifies a
  repository-local or nextmcp-visible pipeline test setup, localizes any needed
  inputs to server-local paths, and converts that setup into a hidden
  evaluation spec for a lightweight test run. In this repository, that spec is
  still called a `smoke contract`.
  Trigger on requests to automatically decide the test mode, reuse the original
  pipeline repository's `nextflow.config`, `conf/test*.config`,
  `tests/nextflow.config`, and `tests/*.nf.test` materials, localize remote
  URLs or `projectDir/tests/...` files when needed, and return a final contract
  plus a user-style prompt brief.
compatibility: >-
  Works with either a repository-local pipeline checkout or a nextmcp-visible
  pipeline whose own test files can be inspected. Requires access to the
  pipeline's `nextflow.config`, `conf/test*.config`, `tests/nextflow.config`,
  `tests/*.nf.test`, `tests/*.snap`, and `.nftignore` when present, plus a
  writable server-local area when localization is needed.
metadata:
  skill-class: meta
  tool-surface: nextmcp
  tool-surface-version: "2026-03-27"
  generated-from: repository pipeline test-contract orchestration rules
---

# Pipeline Test Contract Builder

## Scope

Use this skill as the default top-level entry point when the user wants one pipeline turned into a
ready-to-use hidden evaluation spec in one pass.

This skill orchestrates three lower-level skills:

- `pipeline-test-mode-classifier`
- `pipeline-test-config-localizer`
- `pipeline-test-converter`

Use the lower-level skills directly only when the user wants to inspect one phase in isolation.

## When to use this skill

Use this skill when the user wants one end-to-end pass that chooses the source route, localizes
inputs if needed, and produces the final hidden contract plus the client-visible task prompt.

## What this skill does not handle

- replacing the lower-level skills when the user explicitly wants only classification, localization,
  or conversion
- using repository-added support files such as `tests/pipeline_support/` unless the user asks for
  that alternate source
- turning the client-visible brief into an execution recipe
- judging a completed run after the fact

## Authoritative assets

- `assets/builder-output-schema.yaml`

## References to read next

- `references/01-orchestration-workflow.md`
- `references/02-routing-matrix.md`
- `references/03-output-rendering.md`

## Operating rules

### Output

Return one bundle with these sections:

- `classification`
- `localization`
- `contract`
- `final_status`

Use the schema in `assets/builder-output-schema.yaml`.

### High-level workflow

1. Read the pipeline repository's own test materials.
2. Classify the test setup into one smoke-eval mode.
3. Decide whether localization is required.
4. If localization is required, build the server-local path plan and rewritten manifests.
5. Convert the test setup into the final hidden evaluation spec.
6. Return blockers early when the selected setup is not suitable or cannot be localized.

### Source priority

Use these files in this order:

1. `nextflow.config`
2. `conf/test*.config`
3. `tests/nextflow.config` when needed
4. `tests/*.nf.test`
5. `tests/*.snap` and `.nftignore`

Do not use repository-local support layers such as `tests/pipeline_support/` unless the user
explicitly asks to build contracts from those support materials instead of the pipeline
repository's own test materials.

### Routing rules

### Step 1: Classification

Run the logic from `pipeline-test-mode-classifier`.

Always record:

- `primary_mode`
- `modifiers`
- `evidence`
- `next_action`

### Step 2: Localization decision

Use localization when either of these is true:

- the mode or modifiers imply remote input handling
- `conf/test*.config` or shared test config points at remote URLs or `projectDir/tests/...` files

Skip localization when:

- the selected setup is `unsuitable-for-generic-smoke`
- the selected setup is `requires-local-cache` and the required local roots already exist and
  should stay as they are

For localization behavior, reuse the rules from `pipeline-test-config-localizer`.

Do not assume that a preferred shared mirror root already exists just because a URL matches one
known prefix. When localization is needed, prefer a self-contained bundle under the current
`localized_root` unless the user explicitly said that an external mirror root is authoritative.

### Step 3: Conversion

After classification and optional localization, run the conversion logic from
`pipeline-test-converter`.

The final evaluation spec must include:

- canonical lightweight test setup
- concrete runtime inputs
- server-local path plan
- `nextflow_run(prepare=true)` first-launch plan
- minimal stable assertions
- one user-style prompt brief

The prompt brief is the future client-visible `smoke.task.md`, not an implementation recipe.

### Failure handling

### unsuitable-for-generic-smoke

Return:

- the classification
- an empty localization section
- a `contract` section with blockers only
- `final_status = "skip"`

### missing cache or environment adapter

Return:

- the classification
- the partial localization or validation result
- a partial `contract` section with blockers
- `final_status = "blocked"`

### ready route

Return:

- the classification
- the localization result, or an explicit `not_needed`
- the final `contract` section
- `final_status = "ready"`

### Additional rules

- Keep the top-level output compact. Do not paste large snapshots or long file lists unless the
  user explicitly asks for them.
- Prefer one canonical lightweight test setup, not every test variant in the repository.
- Preserve the reason when shared values from `tests/nextflow.config` are pulled into the setup.
- Treat `.snap` as evidence for minimal assertions, not as a requirement for full snapshot parity.
- When the server configuration can change the original test semantics, such as igenomes handling,
  record that explicitly in classification or blockers.
- Keep the client-visible prompt brief natural. It should describe the task, the available
  server-local inputs, and only the key route constraints that are directly supported by the
  source materials, including concrete resource-cap summaries when the selected test config
  defines them.
- Do not mention internal source file names such as `conf/test.config`, `tests/default.nf.test`,
  `.snap`, or `tests/pipeline_support/...` in the prompt brief.
- Do not mention launch mechanics such as `nextflow_run(prepare=true)`, `config_files`, override
  config paths, or raw Groovy config blocks in the prompt brief.
- When the selected source materials define concrete resource caps, restate them once in plain
  language, for example `keep the upstream test resource caps at 4 CPUs, 15.GB memory, and 1.h
  runtime`.
- Do not frame the prompt brief as a test, validation run, or production analysis unless the user
  explicitly asked for that wording.
- Keep execution mechanics, strict param mapping, and config-scope implementation details in the
  hidden contract, localization data, or secondary agent notes instead of the prompt brief.

### Request-shaping guidance

The prompt-brief rules above are the default behavior of this skill. A caller usually does not need
to restate them in every request.

By default, this skill already assumes that `smoke.task.md` should stay client-visible, brief, and
free of internal file references and execution mechanics.

Ask the user to spell out only the task-specific boundaries that this skill cannot safely guess:

- which pipeline or repository path to process
- which source files are allowed for this task
- which paths, support layers, or server-side presets must be excluded
- which route to prefer when the repository exposes multiple plausible lightweight setups
- any wording override that really differs from the default prompt-brief rules

If the user says `use the default smoke.task.md rules`, treat that as sufficient. Do not ask them
to repeat the built-in brief-format rules unless the request is ambiguous.

## Fast-start workflow

1. Read the pipeline's own test materials in the fixed source order.
2. Classify first.
3. Localize only if the evidence shows it is needed.
4. Convert the chosen setup into one hidden contract.
5. Render a short client-visible brief that says what task to do, what inputs are available, and
   only the source-backed route constraints, including concrete resource-cap summaries when
   present.
