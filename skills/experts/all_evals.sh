#!/usr/bin/env bash
# Run all maintained expert-skill question sets with an explicit Codex model.
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"
model="${NEXTMCP_EVAL_MODEL:-gpt-6-astra}"
iteration="${NEXTMCP_EVAL_ITERATION:-iteration-$(date -u +%Y%m%dT%H%M%SZ)-$$}"
output_root="${NEXTMCP_EVAL_OUTPUT:-$repo_root/evaluation-output}"
pipelines=(fetchngs rnaseq riboseq ampliseq atacseq chipseq epitopeprediction mag methylseq nanoseq rnafusion sarek scrnaseq)
status=0
for pipeline in "${pipelines[@]}"; do
  printf '\nEvaluating %s with %s\n' "$pipeline" "$model"
  if ! uv run python skills/meta/pipeline-expert-skill-creator/scripts/run_offline_evals.py \
    --skill-root "skills/experts/${pipeline}-expert-skill" \
    --workspace "$output_root/${pipeline}-expert-skill-workspace" \
    --iteration "$iteration" --agent codex --model "$model" "$@"; then
    status=1
  fi
done
exit "$status"
