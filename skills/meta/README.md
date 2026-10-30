# Skill authoring and evaluation helpers

These six meta skills help maintain expert skills or prepare and evaluate workflow tasks.
They are optional for ordinary analysis. Install them only on the client where authoring
or evaluation is performed; the NextMCP server does not load them.

## Choose the right helper

| Skill | Input | Action and output | When to use |
| --- | --- | --- | --- |
| [pipeline-expert-skill-creator](pipeline-expert-skill-creator/SKILL.md) | A versioned pipeline checkout or an inspection bundle | Builds instructions, structured assets, references, and offline questions; checks source coverage and recorded gaps | Create or update an expert skill |
| [pipeline-test-mode-classifier](pipeline-test-mode-classifier/SKILL.md) | The pipeline's own test configuration and test files | Records the available test mode, supporting evidence, and blockers | Decide whether a lightweight test is usable |
| [pipeline-test-config-localizer](pipeline-test-config-localizer/SKILL.md) | Test inputs, URLs, manifests, and a destination on the server | Plans or performs input acquisition and rewrites manifests to server-local paths | Prepare data for a test that references remote inputs |
| [pipeline-test-converter](pipeline-test-converter/SKILL.md) | Classified test setup and, when needed, localized inputs | Produces a visible task prompt and a separate hidden evaluation specification | Define what the agent should do and how its run will be checked |
| [pipeline-test-contract-builder](pipeline-test-contract-builder/SKILL.md) | The pipeline's own test materials and a target environment | Coordinates classification, localization, and conversion; reports readiness or blockers | Prepare a complete evaluation task |
| [pipeline-smoke-evaluator](pipeline-smoke-evaluator/SKILL.md) | A hidden specification and evidence from a completed run | Checks task translation, completion, and required outputs | Evaluate an existing run |

A "smoke contract" in existing filenames and skill text means a hidden evaluation
specification for a lightweight workflow test. It is not a server execution API.

## How the test helpers fit together

```text
Official pipeline test materials
  -> classifier: choose the test mode
  -> localizer: prepare server-local inputs when required
  -> converter: write the visible task and hidden specification
  -> executing agent: perform the separately requested analysis
  -> evaluator: compare saved evidence with the hidden specification
```

The contract builder coordinates the first three helpers. Its output contains
classification, localization, contract, and final_status sections. It does not establish
that an analysis ran successfully. Localization can download data and write files; it is
not the same as offline question-based evaluation.

The classifier distinguishes profile-only, profile-plus-tests-config, requires-local-cache,
and unsuitable-for-generic-smoke setups. Its evidence comes from upstream files such as
nextflow.config, conf/test*.config, tests/nextflow.config, and tests/*.nf.test. It does not
assume that every pipeline has a complete or directly reusable test.

The converter separates the task shown to the executing agent from the hidden launch and
output checks. A visible task describes the workflow goal, available inputs, constraints,
and requested deliverables. Resource caps describe the permitted CPU, memory, and runtime
settings for that task; they are not measured resource consumption. Keep the hidden
specification out of the executing agent's context during an ablation comparison.

### Example: prepare a new workflow evaluation task

After installing the builder and its three dependencies, provide a request such as:

```text
Use pipeline-test-contract-builder for the exact upstream release checkout at
/path/to/nf-core-sarek-3.8.1.
Read its own nextflow.config, conf/test*.config, tests/nextflow.config,
tests/*.nf.test, tests/*.snap, and .nftignore when present.
Do not derive the new task from this project's tests/pipeline_support definitions.
Use /srv/testdata/sarek-3.8.1 as the proposed server-local data directory.
Return the classification, localization requirements, visible task, hidden
specification, and blockers. Do not download data or launch Nextflow yet.
```

Replace the paths with actual locations. After reviewing the data plan, explicitly request
localization if needed. Give only the visible task to the analysis agent. Using a new
pipeline release creates a new evaluation condition; it does not reproduce old paper results.

### Example: evaluate a completed run

```text
Use pipeline-smoke-evaluator with the hidden case definition at
tests/pipeline_support/scrnaseq and the completed evidence bundle at
/path/to/saved-run-evidence.
Report task_translated_correctly, run_completed, required_outputs_present,
and the overall result. Report missing evidence instead of inferring it.
Do not rerun the workflow.
```

The minimum evidence is run_request.json, run_result.json, and output_checks.json.
The evaluator returns pass, fail, or insufficient_evidence. Its output-presence check
does not establish biological validity or replace assay-specific QC.

## Generate or update an expert skill

Expert-skill authoring is a separate procedure from constructing workflow evaluation tasks.

1. Select an exact official release and obtain its source materials. Record the release,
   source URL, commit when available, and checksums of files used.
2. Build an authoring bundle from that checkout, or use nextflow_inspect_pipeline with
   material access enabled for a configured local catalogue.
3. Work in a new staging directory. Preserve applicable existing instructions while
   updating parameter names, defaults, input requirements, output conditions, and QC.
4. Record supported capabilities and unresolved or deliberately excluded items, with
   evidence and reasons. Do not describe a resolved item as an open knowledge gap.
5. Run static validation with the matching source bundle, review coverage, and evaluate
   the skill's question set. Review semantic correctness separately from heuristic scores.
6. Review the changes and replace the maintained source package. Back up and replace each
   client installation explicitly; editing this repository alone does not update it.

A checkout used for authoring can live outside this repository. It does not need to be
under nf_pipeline, and using it does not upgrade a server workflow or a previous run.
Inspect nested documentation and relevant modules directly when the bundle omits them.

### Authoring commands

From the repository root in Bash, with the selected release already obtained:

```bash
pipeline_source=/absolute/path/to/nf-core-rnaseq-3.22.2
authoring_dir="$(mktemp -d)"
scripts=skills/meta/pipeline-expert-skill-creator/scripts

uv run python "$scripts/build_authoring_bundle.py" \
  --pipeline "$pipeline_source" --output "$authoring_dir/authoring-bundle.json"

uv run python "$scripts/scaffold_expert_skill.py" \
  --bundle "$authoring_dir/authoring-bundle.json" \
  --output-root "$authoring_dir/rnaseq-expert-skill" --pipeline-version 3.22.2
```

Scaffolding produces a starting package, not a reviewed expert skill. Edit and complete
that staged package before running:

```bash
uv run python "$scripts/validate_expert_skill.py" \
  --bundle "$authoring_dir/authoring-bundle.json" \
  --skill-root "$authoring_dir/rnaseq-expert-skill" \
  --json-output "$authoring_dir/validation.json" \
  --markdown-output "$authoring_dir/validation.md"

uv run python "$scripts/run_offline_evals.py" \
  --skill-root "$authoring_dir/rnaseq-expert-skill" \
  --workspace "$authoring_dir/evaluation-workspace" \
  --agent codex --model gpt-6-astra --iteration review-01
```

For an update, compare the staged source-derived package against the existing package.
Do not scaffold directly over a maintained or installed skill: that can overwrite curated
content. A version label supplied to the scaffold does not verify the checkout's version.

| Script in pipeline-expert-skill-creator/scripts | Role |
| --- | --- |
| build_authoring_bundle.py | Collects local pipeline materials in an inspection-style JSON bundle |
| scaffold_expert_skill.py | Creates an editable initial package |
| generate_schema_groups.py | Converts schema parameters into structured group assets |
| audit_capabilities.py | Checks capability coverage and recorded scope decisions |
| validate_expert_skill.py | Checks package rules, available source coverage, and gap handling |
| run_offline_evals.py | Runs questions through a selected model CLI and produces local heuristic grades |

Validation without a source bundle cannot establish complete coverage of that source.
Offline evaluation means no real workflow execution; the model CLI may contact its service.
Use an evaluation client without live analysis MCP connections. See the
[expert evaluation README](../experts/README.md) for all-13 execution, output files,
model selection, and grading limitations.

## Source packages and installed packages

| Location | Role |
| --- | --- |
| skills/experts/ and skills/meta/ in this repository | Maintained source packages |
| ~/.agents/skills/ on the client | User-wide Codex installation |
| ~/.claude/skills/ on the client | User-wide Claude Code installation |
| evaluation-output/ or a named external workspace | Generated answers, grades, and review records |

Copy the complete selected skill directory, including SKILL.md, assets, and references.
Evaluation questions are retained in the source package; ordinary analysis does not need
to read them. Do not install a workspace, a single SKILL.md by itself, or a parent directory
containing multiple packages as though it were one skill.

For the contract builder, install all four pipeline-test-* packages so their instructions
remain available. Install pipeline-smoke-evaluator separately for post-run review.
The creator is independent of those test helpers. Use the
[main installation instructions](../../README.md#install-on-the-client), replacing the
expert source directory with the selected meta package.

When updating an installed skill, move its existing directory to a dated backup outside
the client's skill-search directories, then copy the reviewed package to the original
destination. Avoid merging over an old package, which can leave obsolete files. Open a
new client session and verify the selected skill before use. No server restart is needed
for a client-only skill update.

Keep these six maintained packages in a source release that supports skill authoring and
evaluation. Runtime-only users can leave them uninstalled.
