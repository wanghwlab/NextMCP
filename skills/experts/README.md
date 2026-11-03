# Expert skill packages

An expert skill supplies pipeline-specific guidance to the client agent. Installation and connection steps are in the
[main README](../../README.md#expert-skills).

## Package contents

| Content | Purpose |
| --- | --- |
| `SKILL.md` | Entry instructions, scope, and runtime rules |
| `assets/` | Parameter definitions, presets, playbooks, output conditions, QC, provenance, and gaps |
| `references/` | Detailed workflow and troubleshooting explanations |
| `evals/evals.json` | Questions, expected answers, assertions, and source references |

Ordinary analysis uses instructions, assets, and references. 
Evaluation questions are maintenance inputs, not runtime input data. 

## Evaluate all 13 skills

From a Bash shell with uv and an authenticated Codex CLI available:

```bash
bash skills/experts/all_evals.sh
```

The script invokes all 13 maintained packages using `--agent codex --model gpt-6-astra`.

Override settings explicitly when needed:

```bash
NEXTMCP_EVAL_MODEL=gpt-6-astra NEXTMCP_EVAL_ITERATION=review-01 bash skills/experts/all_evals.sh
```

PowerShell users example:

```powershell
uv run python skills/meta/pipeline-expert-skill-creator/scripts/run_offline_evals.py --skill-root skills/experts/rnaseq-expert-skill --agent codex --model gpt-6-astra --iteration review-01
```

## Maintain the question sets

This release contains 108 questions across 13 evals/evals.json files. 

## These are the current package targets.

| Pipeline | Version |
| --- | --- |
| fetchngs | 1.12.0 |
| rnaseq | 3.22.2 |
| riboseq | 2.0.0 |
| ampliseq | 2.16.1 |
| atacseq | 2.1.2 |
| chipseq | 2.1.0 |
| epitopeprediction | 3.1.0 |
| mag | 5.4.2 |
| methylseq | 4.2.0 |
| nanoseq | 3.1.0 |
| rnafusion | 4.1.0 |
| sarek | 3.8.1 |
| scrnaseq | 4.1.0 |
