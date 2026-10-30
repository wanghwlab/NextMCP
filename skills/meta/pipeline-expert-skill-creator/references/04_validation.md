# Validation

## Minimum acceptance bar

Before accepting a generated expert skill, confirm:

- layout matches the expected expert package shape
- `frontmatter.name` matches the directory name
- `description` clearly states when the skill should trigger
- assets carry the primary facts
- references are split by use case
- references explain the runtime nextmcp subset the package actually uses
- the package preserves full current-schema parameter coverage through progressive disclosure rather
  than only a partial summary
- the package includes a schema index and grouped parameter assets or references that let the agent
  find one parameter definition without scanning the whole schema at once
- the package includes `assets/capability-audit.yaml` and no high-impact item remains
  `needs_review`
- the package includes `assets/authoring-gaps.yaml` and every gap is `resolved` or `scoped_out`
- when the grouped schema layer was generated, the package keeps the generator inputs or override
  file small and source-backed instead of replacing the whole grouped asset layer with ad hoc hand
  edits
- runtime examples use current tool names such as optional
  `server_info()`, optional `project_list()`, optional `project_get(project)`,
  optional `fs_list(mode="manifest")`, `nextflow_run(prepare=true)`,
  `nextflow_run`, `run_list`, `run_get(include=[...])`, `run_artifacts(...)`,
  `run_logs`, and `fs_read`
- provenance notes say whether authoring used
  `nextflow_inspect_pipeline(detail="materials")` or a repository-local
  inspect-equivalent bundle
- the package states that runtime `path` values, the `project` identifier, and relative path-like
  values in `params` or `config_files` are on the nextmcp server filesystem
- placeholder examples use server-scoped names such as `<server_input_root>/...` when concrete
  server paths are not already known
- ordinary runtime routes do not start with `nextflow_inspect_pipeline`
- the package keeps source-of-truth provenance concise and separate from runtime instructions
- `fs_read` is described as a targeted reader for explicit logs or outputs
- the package explains the `nextflow_run` boundaries for `project`, optional `run_id` /
  `run_name`, `params`, `config_files`, `from_run_id`, and `extra_args`, makes it clear that
  `from_run_id` is the only public restart path, and points to `run_get(detail="full")` for
  `launch_spec`, `nextflow_session_uuid`, and structured resume-compatibility fields instead of
  public resume inputs
- the package makes it clear that project-owned layout paths come from `run_layout` or
  `run_get(detail="full")`, not public inputs
- the package states explicitly that `max_cpus`, `max_memory`, and `max_time` belong in a small
  override config passed through `config_files`, not in `params`
- the package preserves the pipeline's own resource-override syntax when the source uses
  `process.resourceLimits` or another config-level key, instead of inventing `params.max_cpus`
  or `process.maxCpus`
- significant optional capabilities from current schema, docs, and source are either covered or
  explicitly scoped out with a reason
- special runtime prerequisites such as license secrets or server-side databases are not hidden
- alternate entry workflows and major output families are reflected in assets when they matter
- if the pipeline publishes reusable historical outputs, the package teaches
  `artifact_path_contains`, `artifacts.json`, `pipeline_fingerprint`, and a route-confirmation
  step such as `pipeline_info/params.json`
- every current schema parameter appears in one grouped parameter asset or one explicit non-runtime
  bucket with a reason
- grouped parameter assets preserve enough fields for exact lookup and mapping, including group id,
  type, required status, defaults, enum choices, channel, mapping notes, confidence, and mapping
  flags
- the first offline eval set is derived from `evals/templates/expert-skill-evals.json` or explains
  why a different eval shape is needed

## Boundary checks

Reject or revise the package if:

- it reads like a handbook instead of an entrypoint plus references
- it duplicates operator-level tool routing extensively
- it suggests runtime registration inside the nextmcp server
- it copies stale parameter names from legacy skills
- it tells the runtime agent to start by calling `nextflow_inspect_pipeline`
- it presents repository-local authoring as a different payload contract instead of normalizing it
  to the same `schema` / `documents` / `source_files` shape
- it uses bare `local path` wording for runtime path arguments without clarifying that they are
  server-side
- it suggests that client-local paths can be passed directly to nextmcp tools
- it uses `fs_read` as a generic replacement for the packaged pipeline contract
- it skips `run_get(include=[...])` and jumps straight from launch to raw log/file reads
- it keeps only a compact route-shaping parameter summary and drops exact schema-backed lookup
  coverage needed for correct parameter mapping
- it stores the full schema only as one raw blob without a schema index or grouped disclosure path
- it uses ad hoc schema group names without a stable rule or drops parameter fields needed for exact
  mapping
- it tells the runtime agent to recover historical outputs only with broad
  `run_list(... pipeline=...)` scans or guessed outdirs when
  `artifact_path_contains` and named artifacts are available
- it turns `server_info()`, `fs_list(mode="manifest")`, or
  `nextflow_run(prepare=true)` into mandatory boilerplate before every run
- it still uses removed helper names such as `nextflow_get_schema` or `nextflow_get_pipeline`
- it teaches `resume` or `resume_session_id` as public `nextflow_run` inputs instead of using
  `nextflow_run(from_run_id=...)`
- it only documents the default route while silently dropping high-impact optional modes present in
  the current pipeline
- it mentions a special mode in prose but never maps it into presets, playbooks, recipes, or
  artifact contracts
- `validate_expert_skill.py` reports failed machine checks
- `capability-audit.yaml` still has `needs_review` items without coverage or a scope-out reason

## Finishing step

Run `scripts/validate_expert_skill.py` first for machine-checkable layout, schema coverage,
capability coverage, path-boundary, restart-boundary, and authoring-gap checks. Then use this
reference for the remaining manual review. After that, run offline `skill-creator` evals seeded
from `evals/templates/expert-skill-evals.json` unless the user explicitly defers evals. Once the
package passes validation and the chosen eval loop, treat it as a repository-side source package.
Installation still happens on the client side, for example under `./codex/skills/`.

If the package still needs drafting, eval prompts, or iteration, hand that work back to the
general-purpose `skill-creator` skill. This skill does not replace the main skill-authoring loop;
it constrains that loop with nextmcp- and pipeline-specific rules.
