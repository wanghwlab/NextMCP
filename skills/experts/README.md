# Expert skill packages

An expert skill supplies pipeline-specific guidance to the client agent. The MCP server
does not load these packages. Installation and connection steps are in the
[main README](../../README.md#expert-skills).

## Package contents

| Content | Purpose | Keep in the source release? |
| --- | --- | --- |
| `SKILL.md` | Entry instructions, scope, and runtime rules | Yes |
| `assets/` | Parameter definitions, presets, playbooks, output conditions, QC, provenance, and gaps | Yes |
| `references/` | Detailed workflow and troubleshooting explanations | Yes |
| `evals/evals.json` | Questions, expected answers, assertions, and source references | Yes |
| `*-expert-skill-workspace/` | Generated answers, scores, timings, and summaries | No, for this source-only release |
| `*.response.yaml` | A saved answer, where present | No, for this source-only release |

Ordinary analysis uses instructions, assets, and references. Evaluation questions are
maintenance inputs, not runtime input data. Updating a skill does not update the installed
copy until it is copied to the client's skill directory. Back up an existing installation
before replacement, and avoid keeping multiple installed copies with the same skill name.

## Evaluate all 13 skills

From a Bash shell with uv and an authenticated Codex CLI available:

```bash
bash skills/experts/all_evals.sh
```

The script invokes all 13 maintained packages using `--agent codex --model gpt-6-astra`.
It starts independent CLI sessions, not continuations of the current conversation. It
requests that explicit model; access depends on the account and CLI. An unavailable model
is an error, not permission to silently substitute another model.

Override settings explicitly when needed:

```bash
NEXTMCP_EVAL_MODEL=gpt-6-astra NEXTMCP_EVAL_ITERATION=review-01 bash skills/experts/all_evals.sh
```

Check record generation without invoking a model:

```bash
bash skills/experts/all_evals.sh --dry-run
```

Dry-run placeholders deliberately fail grading and return a nonzero exit status. The
batch still visits every package. This is not a failed biological analysis or an evaluated
model score. Normal evaluation also visits all packages and returns nonzero if any fails.

By default, output goes to `evaluation-output/<pipeline>-expert-skill-workspace/<iteration>/`.
The automatically generated iteration name includes UTC time and a process identifier.
`NEXTMCP_EVAL_OUTPUT` selects another output root. Do not overwrite historical evidence.

PowerShell users can run one package directly without Bash:

```powershell
uv run python skills/meta/pipeline-expert-skill-creator/scripts/run_offline_evals.py --skill-root skills/experts/rnaseq-expert-skill --agent codex --model gpt-6-astra --iteration review-01
```

The Python runner's single-package default workspace is beside the source skill; the batch
script explicitly redirects it to `evaluation-output/`. Each iteration records prompts,
answers, local heuristic grades, timing, and summary files. Model identity in the report
is the requested CLI model, not an independent verification of the provider's backend.

To evaluate all 13 from PowerShell without installing Bash, run from the repository root:

```powershell
$iteration = 'iteration-' + (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ') + '-' + $PID
$failedSkills = @()
Get-ChildItem './skills/experts' -Directory -Filter '*-expert-skill' | ForEach-Object {
    uv run python skills/meta/pipeline-expert-skill-creator/scripts/run_offline_evals.py --skill-root $_.FullName --workspace "evaluation-output/$($_.Name)-workspace" --iteration $iteration --agent codex --model gpt-6-astra
    if ($LASTEXITCODE -ne 0) { $failedSkills += $_.Name }
}
if ($failedSkills.Count -gt 0) { throw ('Failed skills: ' + ($failedSkills -join ', ')) }
```

Codex is invoked with a read-only shell sandbox and offline-planning instructions. This
does not make the model service network-free or disable every possible configured client
tool. Use an evaluation client without live analysis MCP connections. No Nextflow run is
part of these question-based checks. The model generates answers; local heuristic rules
score them. A separate semantic review is still required for biological correctness.

Passed results are reused only when the case metadata, requested agent/model, and packaged
skill-content hash match. Use a new iteration after changing evaluation methods. External
CLI/provider defaults can change even if recorded inputs are unchanged.

## Maintain the question sets

This release contains 108 questions across 13 evals/evals.json files. Keep questions aligned
with the version declared by their skill. Do not replace an older release's entire question
set with questions from a newer skill: parameter names, modes, outputs, and prerequisites
may have changed. Merge shared interface corrections only after checking their applicability.

Project examples use my-project, which satisfies the server's identifier rules. Gap questions
must check the current recorded status rather than assume every authoring gap is unresolved.
The RNA-seq custom interactive entry is unavailable unless its matching extension is installed.
Riboseq questions retain explicit Bowtie2 selection and references covering both rRNA and tRNA.

Source-material references such as authoring_bundle.schema identify authoring inputs; they
are not necessarily files inside the installed package. These question sets are maintenance
inputs, not records proving a completed model evaluation or biological analysis.

## Current versions versus Supplementary Table 3

The ten-pipeline panel in Supplementary Table 3 is distinct from the representative cases.
This release uses the paper versions except riboseq, retained at 2.0.0. Version alignment
does not establish that the edited skill text is identical to the original experiment.

| Pipeline | Table 3 | Packaged target | Relationship |
| --- | --- | --- | --- |
| ampliseq | 2.16.1 | 2.16.1 | Paper version target |
| atacseq | 2.1.2 | 2.1.2 | Paper version target |
| chipseq | 2.1.0 | 2.1.0 | Paper version target |
| epitopeprediction | 3.1.0 | 3.1.0 | Paper version target |
| mag | 5.4.2 | 5.4.2 | Paper version target |
| methylseq | 4.2.0 | 4.2.0 | Paper version target |
| nanoseq | 3.1.0 | 3.1.0 | Paper version target |
| riboseq | 1.1.0 | 2.0.0 | Updated skill; not the historical condition |
| rnafusion | 4.1.0 | 4.1.0 | Paper version target |
| scrnaseq | 4.1.0 | 4.1.0 | Paper version target |
| fetchngs | Not in this table | 1.12.0 | Representative-case version |
| rnaseq | Not in this table | 3.22.2 | Representative-case version |
| sarek | Not in this table | 3.8.1 | Representative-case version |

Reproduction also requires the experimental skill revision, inputs, model settings, and run evidence.
