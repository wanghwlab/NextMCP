---
name: pipeline-test-mode-classifier
description: >-
  Use whenever the user wants to classify a repository-local or nextmcp-visible
  pipeline into a smoke-eval extraction mode before building batch system
  evaluations, pipeline support contracts, or large sets of expert skills.
  Trigger on requests to decide whether a pipeline can be run from
  `profile + conf/test*.config`, whether it also depends on
  `tests/nextflow.config`, whether it needs localized remote inputs, local cache
  or environment prerequisites, or whether the original pipeline repository's
  test materials are not suitable
  for a generic nextmcp smoke test.
compatibility: >-
  Works with either a repository-local pipeline checkout such as
  `nf_pipeline/<pipeline>/` or a nextmcp-visible pipeline whose source test
  files can be inspected. Requires access to the pipeline's own
  `nextflow.config`, `conf/test*.config`, `tests/nextflow.config`,
  `tests/*.nf.test`, `tests/*.snap`, and `.nftignore` when present.
metadata:
  skill-class: meta
  tool-surface: nextmcp
  tool-surface-version: "2026-03-27"
  generated-from: repository pipeline test-material classification rules
---

# Pipeline Test Mode Classifier

## Scope

Use this skill to classify one pipeline into a small set of smoke-eval extraction modes that are
useful for batch evaluation across many expert skills.

This skill is for triage and test-setup selection. It does not localize inputs, build final
prompts, or run the pipeline by itself.

## When to use this skill

Use this skill when the user wants to know which test-material route should be used before
building a hidden evaluation spec:

- runtime config alone
- runtime config plus `tests/nextflow.config`
- prelocalized local cache
- skip because the upstream test setup is not a good generic fit

## What this skill does not handle

- downloading or rewriting remote inputs
- building the final hidden contract bundle
- writing the client-visible `smoke.task.md`
- rerunning the pipeline or judging a finished run

## Authoritative assets

- `assets/classification-schema.yaml`

## References to read next

- `references/01-classification-rubric.md`
- `references/02-evidence-collection.md`
- `references/03-worked-examples.md`

## Operating rules

### Output

Return a compact classification with these fields:

- `primary_mode`
- `modifiers`
- `evidence`
- `next_action`

Use the schema in `assets/classification-schema.yaml`.

### Primary modes

Use one primary mode only:

- `profile-only`
  The smoke task can be derived from the pipeline runtime config chain, usually
  `nextflow.config` plus `conf/test*.config`.
- `profile-plus-tests-config`
  The smoke task still comes from the pipeline runtime config, but shared values in
  `tests/nextflow.config` are also needed to reconstruct the original test setup.
- `requires-local-cache`
  The current repository test setup assumes prelocalized or predownloaded server-local files such
  as `/data/...`, so it is not a generic remote-first smoke test.
- `unsuitable-for-generic-smoke`
  The pipeline repository's own test materials are too tied to nf-test internals, external
  licenses, private services, or missing local state to recommend as a standard nextmcp smoke
  setup.

### Modifiers

Add zero or more modifiers:

- `localize-remote-inputs`
- `environment-sensitive`
- `igenome-sensitive`
- `snapshot-rich`

Use the definitions in `assets/classification-schema.yaml`.

### Evidence order

Collect evidence in this order:

1. `nextflow.config`
2. `conf/test*.config`
3. `tests/nextflow.config` when needed
4. `tests/*.nf.test`
5. `tests/*.snap` and `.nftignore` when needed for stable-output evidence

Do not use repository-added support layers such as `tests/pipeline_support/` unless the user
explicitly asks to classify those materials instead of the pipeline repository's own test
materials.

### Workflow

1. Find the canonical lightweight test entry from the pipeline repository.
   Prefer `test`, else the smallest `test_*` profile that still represents a normal pipeline run.
2. Decide the primary mode.
   Use `profile-only` when runtime config is enough.
   Escalate to `profile-plus-tests-config` when shared params or test-only base paths live in
   `tests/nextflow.config`.
   Use `requires-local-cache` when the current repo already points at fixed server-local cache
   paths.
   Use `unsuitable-for-generic-smoke` when no stable generic test setup is visible.
3. Add modifiers.
   Add `localize-remote-inputs` when inputs or references come from remote URLs or manifests with
   nested remote URLs.
   Add `environment-sensitive` when licenses, cloud auth, private datasets, or runtime-only network
   behavior materially affect reproducibility.
   Add `igenome-sensitive` when the selected test setup depends on `genome` / igenomes resolution
   and the server may override that path.
   Add `snapshot-rich` when `.snap` and `.nftignore` provide enough stable artifact evidence to
   derive a small assertion set.
4. Produce the next action.
   Recommend one of:
   `build smoke contract from runtime config`,
   `merge tests/nextflow.config into extraction`,
   `localize inputs first`,
   `require environment adapter`,
   or `skip from standard batch`.

## Fast-start workflow

1. Read the pipeline's own runtime test files in the fixed evidence order.
2. Pick one primary mode only.
3. Add only the modifiers that materially change the next step.
4. Return a short evidence-backed `next_action` so the caller knows whether to localize, convert,
   or skip.
