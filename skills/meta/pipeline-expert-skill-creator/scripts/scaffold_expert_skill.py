"""Scaffold a minimal editable pipeline expert skill from an authoring bundle."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

import yaml

from nextmcp.nextflow_schema import flatten_nextflow_schema

SCRIPT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = SCRIPT_DIR.parent / "assets"
FRONTMATTER_TEMPLATE_PATH = ASSETS_DIR / "templates" / "frontmatter.yaml"
SCHEMA_GROUP_GENERATOR_PATH = SCRIPT_DIR / "generate_schema_groups.py"
CAPABILITY_AUDIT_PATH = SCRIPT_DIR / "audit_capabilities.py"
RUNTIME_TOOL_NAMES = (
    "server_info",
    "project_list",
    "project_get",
    "fs_list",
    "nextflow_run",
    "run_list",
    "run_get",
    "run_artifacts",
    "run_logs",
    "fs_read",
    "nextflow_list_pipelines",
)
SCAFFOLD_LIMITATIONS = (
    "Starter scaffold only. Review current docs and outputs before runtime use.",
    "Confirm special runtime prerequisites such as licenses, indices, or server-local databases.",
)


def scaffold_expert_skill(
    bundle: dict[str, Any],
    *,
    output_root: Path,
    pipeline_version: str,
    schema_group_overrides: dict[str, Any] | None,
) -> None:
    """Write one minimal expert skill scaffold from an inspect-style authoring bundle."""
    pipeline_id = _require_string(bundle, "pipeline_id")
    skill_name = f"{pipeline_id}-expert-skill"
    if output_root.name != skill_name:
        raise ValueError(
            f"output root must end with {skill_name!r} so generated frontmatter matches "
            "the directory name"
        )

    schema = bundle.get("schema")
    if not isinstance(schema, dict):
        raise ValueError("authoring bundle must include a parsed `schema` object")

    generator = _load_schema_group_generator()
    auditor = _load_capability_auditor()
    artifacts = generator.generate_schema_group_artifacts(
        schema,
        pipeline_id=pipeline_id,
        overrides=schema_group_overrides,
        write_reference_drafts=True,
    )
    capability_audit = auditor.audit_capabilities(bundle)
    generator.write_schema_group_artifacts(
        output_root=output_root,
        schema_index=artifacts["schema_index"],
        group_payloads=artifacts["group_payloads"],
        reference_drafts=artifacts["reference_drafts"],
    )

    display_name = _display_name(bundle)
    pipeline_summary = _pipeline_summary(bundle)
    grouped_parameters = _parameter_map(artifacts["group_payloads"])
    flattened = flatten_nextflow_schema(schema)
    required_inputs = _required_inputs(flattened, grouped_parameters)
    default_placeholders = _default_placeholders(required_inputs)
    supported_modes = _supported_modes(bundle, pipeline_id)
    playbooks = _playbooks(required_inputs, bundle)
    steps = _step_recipes(required_inputs, pipeline_id)
    authoring_gaps = _authoring_gaps(capability_audit)
    frontmatter = _frontmatter(
        bundle=bundle,
        skill_name=skill_name,
        pipeline_id=pipeline_id,
        pipeline_version=pipeline_version,
        display_name=display_name,
    )

    _write_text(output_root / "SKILL.md", _render_skill_md(frontmatter, display_name))
    _write_yaml(
        output_root / "assets" / "pipeline-profile.yaml",
        {
            "pipeline": {
                "id": pipeline_id,
                "name": display_name,
                "version": pipeline_version,
                "summary": pipeline_summary,
            },
            "source_basis": _source_basis(bundle),
            "required_inputs": required_inputs,
            "supported_modes": supported_modes,
            "limitations": list(SCAFFOLD_LIMITATIONS),
        },
    )
    _write_yaml(output_root / "assets" / "playbooks.yaml", {"playbooks": playbooks})
    _write_yaml(output_root / "assets" / "capability-audit.yaml", capability_audit)
    _write_yaml(output_root / "assets" / "authoring-gaps.yaml", authoring_gaps)
    _write_yaml(output_root / "assets" / "step-recipes.yaml", {"steps": steps})
    _write_yaml(
        output_root / "assets" / "param-presets.yaml",
        {
            "presets": {
                "default_run": {
                    "use_when": (
                        "Starting point for a standard run after the user confirms "
                        "the server-local inputs."
                    ),
                    "params": {},
                    "placeholders": default_placeholders,
                }
            }
        },
    )
    _write_yaml(
        output_root / "assets" / "artifact-contracts.yaml",
        {
            "artifacts": [
                {
                    "id": "results_root",
                    "path": "results/<run_id>/",
                    "produced_when": "The main pipeline entry finishes successfully.",
                    "meaning": "Primary published results root for review and downstream handoff.",
                }
            ]
        },
    )
    _write_yaml(
        output_root / "assets" / "qc-rules.yaml",
        {
            "checks": [
                {
                    "id": "run_completion",
                    "severity": "high",
                    "source": 'run_get(include=["progress","diagnosis","artifact_summary"])',
                    "good_signal": "Run succeeded and published the expected results root.",
                    "bad_signal": "Run failed, stalled, or reported a blocking diagnosis.",
                    "action": "Check run logs first, then inspect the relevant output section.",
                }
            ]
        },
    )

    _write_text(
        output_root / "references" / "01_scope_and_assumptions.md",
        _render_scope_reference(bundle=bundle, pipeline_id=pipeline_id, display_name=display_name),
    )
    _write_text(
        output_root / "references" / "02_playbooks.md", _render_playbooks_reference(playbooks)
    )
    _write_text(
        output_root / "references" / "03_parameters.md",
        _render_parameters_reference(required_inputs, default_placeholders),
    )
    _write_text(
        output_root / "references" / "04_schema_lookup.md",
        _render_schema_lookup_reference(artifacts["schema_index"]),
    )
    _write_text(
        output_root / "references" / "05_outputs_and_qc.md",
        _render_outputs_reference(),
    )
    _write_text(
        output_root / "references" / "06_troubleshooting.md",
        _render_troubleshooting_reference(),
    )
    _write_json(
        output_root / "evals" / "evals.json",
        _offline_evals(
            pipeline_id=pipeline_id,
            display_name=display_name,
            required_inputs=required_inputs,
            capability_audit=capability_audit,
            authoring_gaps=authoring_gaps,
        ),
    )


def _load_schema_group_generator() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pipeline_expert_skill_creator_schema_group_generator",
        SCHEMA_GROUP_GENERATOR_PATH,
    )
    if spec is None or spec.loader is None:
        raise ValueError(
            f"Could not load schema group generator from {SCHEMA_GROUP_GENERATOR_PATH}"
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_capability_auditor() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pipeline_expert_skill_creator_capability_auditor",
        CAPABILITY_AUDIT_PATH,
    )
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load capability auditor from {CAPABILITY_AUDIT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _frontmatter(
    *,
    bundle: dict[str, Any],
    skill_name: str,
    pipeline_id: str,
    pipeline_version: str,
    display_name: str,
) -> dict[str, Any]:
    template = yaml.safe_load(FRONTMATTER_TEMPLATE_PATH.read_text(encoding="utf-8"))
    if not isinstance(template, dict):
        raise ValueError("frontmatter template must be a mapping")
    return {
        "name": skill_name,
        "description": (
            f"Use when the user wants to plan, run, interpret, or troubleshoot {display_name} "
            "analyses through nextmcp, especially for server-local inputs, "
            "route-shaping params, outputs, or reruns."
        ),
        "compatibility": template["compatibility"],
        "metadata": {
            "skill-class": "expert",
            "pipeline-id": pipeline_id,
            "pipeline-version": pipeline_version,
            "generated-from": _generated_from(bundle),
        },
    }


def _display_name(bundle: dict[str, Any]) -> str:
    schema_summary = bundle.get("schema_summary")
    if isinstance(schema_summary, dict):
        title = schema_summary.get("title")
        if isinstance(title, str) and title.strip():
            return title.strip()
    return _humanize_identifier(_require_string(bundle, "pipeline_id"))


def _pipeline_summary(bundle: dict[str, Any]) -> str:
    schema_summary = bundle.get("schema_summary")
    if isinstance(schema_summary, dict):
        description = schema_summary.get("description")
        if isinstance(description, str) and description.strip():
            return description.strip()
    return "Pipeline scaffold for nextmcp planning, launch, and result review."


def _generated_from(bundle: dict[str, Any]) -> str:
    pipeline_dir = bundle.get("pipeline_dir")
    if isinstance(pipeline_dir, str) and pipeline_dir.strip():
        return f"authoring bundle rooted at {pipeline_dir.strip()}"
    return "authoring bundle"


def _source_basis(bundle: dict[str, Any]) -> list[str]:
    pipeline_dir = bundle.get("pipeline_dir")
    basis = ["authoring bundle fields: schema, documents, and source_files"]
    if isinstance(pipeline_dir, str) and pipeline_dir.strip():
        basis.append(f"pipeline directory: {pipeline_dir.strip()}")
    return basis


def _authoring_gaps(capability_audit: dict[str, Any]) -> dict[str, Any]:
    capabilities = capability_audit.get("capabilities")
    needs_review = (
        [
            {
                "id": item.get("id"),
                "source": "capability-audit.yaml",
                "status": "open",
                "action": (
                    "Cover this capability in the listed assets or mark it scoped out "
                    "with a reason."
                ),
            }
            for item in capabilities
            if isinstance(item, dict) and item.get("status") == "needs_review"
        ]
        if isinstance(capabilities, list)
        else []
    )
    needs_review.extend(
        [
            {
                "id": "replace_generic_artifact_contract",
                "source": "artifact-contracts.yaml",
                "status": "open",
                "action": (
                    "Replace the generic results-root contract with source-backed "
                    "published outputs."
                ),
            },
            {
                "id": "replace_generic_qc_rule",
                "source": "qc-rules.yaml",
                "status": "open",
                "action": (
                    "Replace the generic completion check with source-backed QC and "
                    "troubleshooting rules."
                ),
            },
        ]
    )
    return {
        "status": "open" if needs_review else "resolved",
        "gaps": needs_review,
    }


def _parameter_map(group_payloads: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    parameters: dict[str, dict[str, Any]] = {}
    for payload in group_payloads.values():
        for parameter in payload["parameters"]:
            parameters[parameter["name"]] = parameter
    return parameters


def _required_inputs(
    flattened: Any,
    parameters: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    names = [name for name in flattened.properties if name in flattened.required]
    if "outdir" in flattened.properties and "outdir" not in names:
        names.append("outdir")

    required_inputs: list[dict[str, str]] = []
    for name in names:
        parameter = parameters[name]
        placeholder = parameter.get("placeholder") or "<set_on_server>"
        description = str(parameter.get("description") or "Fill from the current schema.")
        required_inputs.append(
            {
                "name": name,
                "required_for": "Most runs" if name != "outdir" else "Published results",
                "placeholder": placeholder,
                "notes": description,
            }
        )
    return required_inputs


def _default_placeholders(required_inputs: list[dict[str, str]]) -> dict[str, str]:
    placeholders: dict[str, str] = {}
    for item in required_inputs:
        placeholder = item["placeholder"]
        if placeholder != "<set_on_server>":
            placeholders[item["name"]] = placeholder
    return placeholders


def _supported_modes(bundle: dict[str, Any], pipeline_id: str) -> list[dict[str, Any]]:
    modes = [
        {
            "id": "main_entry",
            "entry_target": f"pipeline id {pipeline_id}",
            "use_when": "Standard main pipeline route.",
        }
    ]
    if _has_interactive_entry(bundle):
        modes.append(
            {
                "id": "alternate_entry",
                "entry_target": "explicit server-local pipeline path",
                "use_when": "Alternate entry script route.",
            }
        )
    return modes


def _has_interactive_entry(bundle: dict[str, Any]) -> bool:
    source_files = bundle.get("source_files")
    if not isinstance(source_files, list):
        return False
    for item in source_files:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        if isinstance(path, str) and path.endswith("interactive.nf"):
            return True
    return False


def _playbooks(
    required_inputs: list[dict[str, str]], bundle: dict[str, Any]
) -> list[dict[str, Any]]:
    prerequisites = [f"Confirm `{item['name']}` on the nextmcp server." for item in required_inputs]
    playbooks = [
        {
            "id": "default_run",
            "use_when": "Standard pipeline route.",
            "prerequisites": prerequisites,
            "recommended_preset": "default_run",
            "outputs_to_review": ["results/<run_id>/"],
        }
    ]
    if _has_interactive_entry(bundle):
        playbooks.append(
            {
                "id": "alternate_entry",
                "use_when": "Alternate entry script route.",
                "prerequisites": [
                    "Resolve the exact server-local pipeline path.",
                    "Confirm the entry-specific inputs.",
                ],
                "recommended_preset": "default_run",
                "outputs_to_review": ["results/<run_id>/", "run layout details"],
            }
        )
    return playbooks


def _step_recipes(required_inputs: list[dict[str, str]], pipeline_id: str) -> list[dict[str, Any]]:
    minimal_inputs = ["project"] + [item["name"] for item in required_inputs]
    return [
        {
            "id": "launch",
            "purpose": "Confirm inputs, launch the pipeline, then inspect status before raw files.",
            "minimal_inputs": minimal_inputs,
            "tool_sequence": [
                "project_list() when the project id is unknown",
                "project_get(project) when the project root or prior runs matter",
                'fs_list(mode="manifest") when one server path still needs confirmation',
                "nextflow_run(prepare=true) when launch layout is still uncertain",
                f'nextflow_run(pipeline="{pipeline_id}", project=..., params=...)',
                'run_get(include=["progress","artifact_summary","diagnosis","next_actions"])',
                "run_logs() or fs_read() after the path is known",
            ],
            "outputs": [
                "run layout",
                "results/<run_id>/",
                "status summary",
            ],
        }
    ]


def _render_skill_md(frontmatter: dict[str, Any], display_name: str) -> str:
    header = yaml.safe_dump(frontmatter, sort_keys=False).strip()
    tool_list = ", ".join(RUNTIME_TOOL_NAMES)
    lines = [
        "---",
        header,
        "---",
        "",
        f"# {display_name} Expert Skill",
        "",
        "## Scope",
        "",
        f"Compact starter scaffold for `{display_name}` through nextmcp.",
        "",
        "## When to use this skill",
        "",
        "- the user wants help planning, launching, interpreting, or troubleshooting this pipeline",
        "- the user needs exact parameter lookup from packaged schema assets",
        "",
        "## What this skill does not handle",
        "",
        "- finished downstream interpretation beyond the pipeline's own outputs",
        "- infrastructure setup or production guarantees before source-backed refinement",
        "",
        "## Authoritative assets",
        "",
        "- `assets/pipeline-profile.yaml`: identity, supported modes, assumptions, and limits. "
        "Read first when deciding whether this skill covers the user's request.",
        "- `assets/playbooks.yaml`: user-intent routes and decision rules. Read when choosing a "
        "standard, special-mode, or troubleshooting route.",
        "- `assets/step-recipes.yaml`: step-level prerequisites, entry scripts, outputs, and "
        "failure checks. Read when planning a partial run or explaining a workflow stage.",
        "- `assets/param-presets.yaml`: reusable launch parameter bundles. Read before drafting "
        "`nextflow_run` arguments.",
        "- `assets/schema-index.yaml`: lightweight map from parameter names and groups to the "
        "full schema files. Read when an exact parameter name, type, default, or enum matters.",
        "- `assets/schema-groups/*.yaml`: exact grouped parameter definitions from the current "
        "schema. Read only the group named by `schema-index.yaml`.",
        "- `assets/capability-audit.yaml`: high-impact capabilities found during authoring and "
        "their coverage status. Read while maintaining or reviewing the skill, not for normal "
        "runtime planning unless coverage is uncertain.",
        "- `assets/authoring-gaps.yaml`: unresolved scaffold gaps and scoped-out items. Read "
        "before treating this package as complete or when an answer depends on a listed gap.",
        "- `assets/artifact-contracts.yaml`: expected output families, handoff files, and review "
        "order. Read after a run finishes or when planning historical reuse.",
        "- `assets/qc-rules.yaml`: QC checks, thresholds, and interpretation notes. Read when the "
        "user asks whether outputs look usable.",
        "",
        "## References to read next",
        "",
        "- `references/01_scope_and_assumptions.md`: human-readable scope, source basis, and "
        "known limits. Read when deciding whether the user request is in scope.",
        "- `references/02_playbooks.md`: route narratives and workflow choices. Read when the "
        "asset route needs explanation for a user.",
        "- `references/03_parameters.md`: compact parameter guide, placeholders, and "
        "`params` versus `config_files` boundaries. Read before preparing a launch plan.",
        "- `references/04_schema_lookup.md`: how to use `schema-index.yaml` and grouped schema "
        "references. Read when a field requires exact schema-backed lookup.",
        "- `references/05_outputs_and_qc.md`: output review order and QC interpretation. Read "
        "after `run_get` and `run_artifacts` identify concrete sections or files.",
        "- `references/06_troubleshooting.md`: common failures and recovery routes. Read after "
        "summary or logs show a failure mode.",
        "",
        "## Operating rules",
        "",
        "- Treat this as a starter scaffold until `assets/authoring-gaps.yaml` has no open gaps.",
        "- Resolve each `needs_review` item in `assets/capability-audit.yaml` before runtime use.",
        "- Use packaged assets first. Do not start runtime planning with "
        "`nextflow_inspect_pipeline`.",
        "- All `path` values, `project`, and relative path-like values in `params` or "
        "`config_files` refer to the nextmcp server filesystem.",
        f"- The runtime tool subset for this scaffold is: `{tool_list}`.",
        "- Use `run_get(include=[...])` before `run_logs` or `fs_read` after launch.",
        "",
        "## Fast-start playbooks",
        "",
        "1. Read `assets/playbooks.yaml` to choose the route.",
        "2. Read `references/03_parameters.md` for required placeholders and the default preset.",
        "3. Use `references/04_schema_lookup.md` only when exact field mapping matters.",
        "",
    ]
    return "\n".join(lines)


def _render_scope_reference(
    *,
    bundle: dict[str, Any],
    pipeline_id: str,
    display_name: str,
) -> str:
    source_basis = _source_basis(bundle)
    lines = [
        "# Scope And Assumptions",
        "",
        f"Runtime scaffold for `{display_name}` built from authoring materials.",
        "",
        "## Source Basis",
        "",
    ]
    lines.extend(f"- {item}" for item in source_basis)
    lines.extend(
        [
            "",
            "## Runtime Boundaries",
            "",
            f'- Treat `pipeline="{pipeline_id}"` as the default pipeline id route.',
            "- Do not call `nextflow_inspect_pipeline` during ordinary runtime planning or launch.",
            "- All runtime paths must already exist on the nextmcp server or come from "
            "nextmcp outputs.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_playbooks_reference(playbooks: list[dict[str, Any]]) -> str:
    lines = [
        "# Playbooks",
        "",
    ]
    for playbook in playbooks:
        lines.extend(
            [
                f"## {playbook['id']}",
                "",
                playbook["use_when"],
                "",
                "Prerequisites:",
            ]
        )
        lines.extend(f"- {item}" for item in playbook["prerequisites"])
        lines.extend(
            [
                "",
                f"- Preset: `{playbook['recommended_preset']}`",
                "",
            ]
        )
    return "\n".join(lines)


def _render_parameters_reference(
    required_inputs: list[dict[str, str]],
    default_placeholders: dict[str, str],
) -> str:
    lines = [
        "# Parameters",
        "",
        "Use `default_run` first. Replace every placeholder with a server-local value.",
        "",
        "## Required Inputs",
        "",
    ]
    for item in required_inputs:
        lines.extend(
            [
                f"- `{item['name']}`: {item['notes']}",
                f"  Placeholder: `{item['placeholder']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Default Preset",
            "",
        ]
    )
    if default_placeholders:
        lines.extend(f"- `{name}` -> `{value}`" for name, value in default_placeholders.items())
    else:
        lines.append("- Add server-local placeholders after reviewing the grouped schema assets.")
    lines.extend(
        [
            "",
            "## Exact Lookup",
            "",
            "- Use `assets/schema-index.yaml` to choose the right schema group.",
            "- Open the matching grouped reference before the YAML when that is enough.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_schema_lookup_reference(schema_index: dict[str, Any]) -> str:
    lines = [
        "# Schema Lookup",
        "",
        f"- Grouping strategy: {schema_index['grouping_strategy']}",
        "",
        "## Groups",
        "",
    ]
    for group in schema_index["groups"]:
        lines.extend(
            [
                f"- `{group['id']}`: {group['summary']}",
                f"  Use when: {group['use_when']}",
                f"  Reference: `{group['reference_path']}`",
                f"  Asset: `{group['asset_path']}`",
            ]
        )
    return "\n".join(lines)


def _render_outputs_reference() -> str:
    return "\n".join(
        [
            "# Outputs And QC",
            "",
            "Start with `assets/artifact-contracts.yaml` and `assets/qc-rules.yaml`.",
            "- Replace the generic results-root entry with the real published output families.",
            '- Review `run_get(include=["artifact_summary"])` before reading individual files.',
            "",
        ]
    )


def _render_troubleshooting_reference() -> str:
    return "\n".join(
        [
            "# Troubleshooting",
            "",
            '- Start with `run_get(include=["progress","diagnosis","next_actions"])`.',
            "- Use `run_logs()` when the summary is not enough.",
            "- Use `fs_read()` only for one explicit file after you know the path.",
            "- Use `from_run_id` as the only public restart path when rerun planning matters.",
            "",
        ]
    )


def _offline_evals(
    *,
    pipeline_id: str,
    display_name: str,
    required_inputs: list[dict[str, str]],
    capability_audit: dict[str, Any],
    authoring_gaps: dict[str, Any],
) -> dict[str, Any]:
    """Build one mixed-source offline eval set for the generated expert skill."""
    evals = [
        _parameter_channel_eval(pipeline_id=pipeline_id, display_name=display_name),
        _required_input_schema_eval(
            pipeline_id=pipeline_id,
            display_name=display_name,
            required_inputs=required_inputs,
        ),
        _outputs_qc_eval(pipeline_id=pipeline_id, display_name=display_name),
        _historical_reuse_eval(pipeline_id=pipeline_id, display_name=display_name),
    ]
    capability_evals = _capability_coverage_evals(
        pipeline_id=pipeline_id,
        display_name=display_name,
        capability_audit=capability_audit,
    )
    evals.extend(capability_evals)
    covered_gap_ids = {
        item["id"].removeprefix("source-coverage-").replace("-", "_")
        for item in capability_evals
        if isinstance(item.get("id"), str)
    }
    evals.extend(
        _gap_negative_scope_evals(
            pipeline_id=pipeline_id,
            display_name=display_name,
            authoring_gaps=authoring_gaps,
            covered_gap_ids=covered_gap_ids,
        )
    )
    return {
        "template_name": "pipeline-expert-skill-offline-evals",
        "template_version": "v2",
        "purpose": (
            f"Mixed-source offline evals for {pipeline_id}-expert-skill. These evals test "
            "runtime planning, parameter mapping, route selection, output review, historical "
            "reuse, and source-backed coverage without launching Nextflow."
        ),
        "usage": {
            "run_mode": "offline",
            "nextflow_launch_required": False,
            "expected_output_format": "structured plan or YAML-like summary, not a real launch",
            "sources": {
                "asset": "Tests whether the agent uses packaged expert skill assets correctly.",
                "authoring_bundle": (
                    "Tests whether source-derived facts are covered or explicitly scoped out."
                ),
                "audit": "Tests high-impact capability and authoring-gap handling.",
            },
        },
        "summary": {
            "asset_eval_count": sum(1 for item in evals if item["source"] == "asset"),
            "authoring_bundle_eval_count": sum(
                1 for item in evals if item["source"] == "authoring_bundle"
            ),
            "audit_eval_count": sum(1 for item in evals if item["source"] == "audit"),
        },
        "evals": evals,
    }


def _parameter_channel_eval(*, pipeline_id: str, display_name: str) -> dict[str, Any]:
    return {
        "id": "parameter-channel-mapping",
        "source": "asset",
        "category": "parameter_mapping",
        "source_materials": [
            "assets/param-presets.yaml",
            "references/03_parameters.md",
            "SKILL.md",
        ],
        "prompt": (
            f"Using the {pipeline_id}-expert-skill, draft the nextmcp launch plan for "
            f"{display_name}. The project is my-project. The user confirmed the server-local "
            f"input at /data/samplesheet.csv and wants results under /results/{pipeline_id}. "
            "They also asked to cap the run at 8 CPUs and 32 GB memory. Do not launch the run; "
            "return only the planned tool order and the nextflow_run argument shape."
        ),
        "expected_output": (
            "A launch plan that keeps project as a top-level nextflow_run argument, puts ordinary "
            "pipeline options under params, puts resource caps in a server-local override config "
            "passed through config_files, omits profile by default, and avoids "
            "nextflow_inspect_pipeline."
        ),
        "assertions": [
            "Mentions project as a top-level nextflow_run argument, not inside params.",
            "Mentions input and outdir under params.",
            "Mentions max_cpus/max_memory or resource caps under config_files or an "
            "override config, not params.",
            "Does not use nextflow_inspect_pipeline for runtime planning.",
            "Uses nextflow_run(prepare=true) only as an optional check when launch "
            "uncertainty remains.",
        ],
        "files": [],
    }


def _required_input_schema_eval(
    *,
    pipeline_id: str,
    display_name: str,
    required_inputs: list[dict[str, str]],
) -> dict[str, Any]:
    required_names = [item["name"] for item in required_inputs] or ["input", "outdir"]
    joined_names = ", ".join(required_names)
    return {
        "id": "source-coverage-required-inputs",
        "source": "authoring_bundle",
        "category": "coverage",
        "source_materials": [
            "authoring_bundle.schema",
            "assets/schema-index.yaml",
            "assets/schema-groups/*.yaml",
            "references/03_parameters.md",
        ],
        "prompt": (
            f"Using the {pipeline_id}-expert-skill, explain how to prepare a dry run for "
            f"{display_name} when the source schema requires or commonly uses these fields: "
            f"{joined_names}. Do not launch anything. State which schema lookup assets you would "
            "open to confirm exact names, defaults, and placeholder values."
        ),
        "expected_output": (
            "A schema-backed preparation plan that mentions the required or common input fields, "
            "uses schema-index.yaml plus the matching schema group for exact lookup, and keeps "
            "server-local paths inside params."
        ),
        "assertions": [
            "Uses schema-index or grouped schema assets for exact mapping when needed.",
            "Mentions input and outdir under params.",
            "Does not use nextflow_inspect_pipeline for runtime planning.",
            "Does not invent unsupported enum values or parameter names.",
        ],
        "files": [],
    }


def _outputs_qc_eval(*, pipeline_id: str, display_name: str) -> dict[str, Any]:
    return {
        "id": "outputs-and-qc-review",
        "source": "asset",
        "category": "outputs_qc",
        "source_materials": [
            "assets/artifact-contracts.yaml",
            "assets/qc-rules.yaml",
            "references/05_outputs_and_qc.md",
        ],
        "prompt": (
            f"Using the {pipeline_id}-expert-skill, answer a user who says: 'The "
            f"{display_name} run finished, and I need to review the main published outputs and "
            "QC reports. What nextmcp calls should I make first, and which artifact or report "
            "paths should I inspect?' Do not assume concrete paths that have not come from "
            "nextmcp."
        ),
        "expected_output": (
            'A post-run review plan that starts with run_get(include=["progress",'
            '"artifact_summary","diagnosis","next_actions"]), then uses run_artifacts for '
            "relevant sections, then fs_read only for explicit report or table paths. It should "
            "use artifact contracts and QC rules instead of guessing output paths."
        ),
        "assertions": [
            'Starts with run_get(include=["progress","artifact_summary","diagnosis",'
            '"next_actions"]) or equivalent summary-first call.',
            "Uses run_artifacts before reading individual output files.",
            "Uses fs_read only after an explicit path is known.",
            "Grounds output choices in artifact-contracts.yaml or QC rules.",
            "Does not jump straight to raw logs as the default first step.",
        ],
        "files": [],
    }


def _historical_reuse_eval(*, pipeline_id: str, display_name: str) -> dict[str, Any]:
    return {
        "id": "historical-reuse",
        "source": "asset",
        "category": "historical_reuse",
        "source_materials": [
            "assets/artifact-contracts.yaml",
            "references/05_outputs_and_qc.md",
            "SKILL.md",
        ],
        "prompt": (
            f"Using the {pipeline_id}-expert-skill, plan how to recover a previous "
            f"{display_name} run when the user only remembers one output filename fragment. "
            "The project is my-project. Do not launch anything; return the search and "
            "compatibility-check sequence."
        ),
        "expected_output": (
            f"A historical reuse plan that searches with run_list(project=..., "
            f'pipeline="{pipeline_id}", artifact_path_contains=...), inspects '
            'run_get(include=["artifact_summary"]), uses run_artifacts, treats artifacts.json '
            "and pipeline_fingerprint as historical facts, and confirms route compatibility "
            "through pipeline_info/params.json or equivalent metadata before recommending reuse."
        ),
        "assertions": [
            "Uses run_list with artifact_path_contains when only an artifact fragment is known.",
            'Uses run_get(include=["artifact_summary"]) before run_artifacts.',
            "Mentions artifacts.json or pipeline_fingerprint as historical facts.",
            "Requires route compatibility confirmation through pipeline_info/params.json "
            "or equivalent metadata.",
            "Does not guess old output directories as the default safe path.",
        ],
        "files": [],
    }


def _capability_coverage_evals(
    *,
    pipeline_id: str,
    display_name: str,
    capability_audit: dict[str, Any],
) -> list[dict[str, Any]]:
    capabilities = capability_audit.get("capabilities")
    if not isinstance(capabilities, list):
        return []
    selected = _diverse_capability_eval_items(capabilities)
    evals = []
    for item in selected:
        capability_id = str(item.get("id") or "unknown")
        capability_kind = str(item.get("kind") or "capability")
        required_assets = item.get("required_assets")
        if not isinstance(required_assets, list):
            required_assets = []
        evidence = item.get("evidence")
        source_materials = _evidence_materials(evidence)
        source_materials.extend(
            f"assets/{asset}" for asset in required_assets if isinstance(asset, str)
        )
        evals.append(
            {
                "id": f"source-coverage-{_slug(capability_id)}",
                "source": "authoring_bundle",
                "category": "coverage",
                "source_materials": sorted(set(source_materials)),
                "prompt": (
                    f"Using the {pipeline_id}-expert-skill, decide whether this source-derived "
                    f"{display_name} {capability_kind.replace('_', ' ')} capability is covered "
                    f"for runtime planning: {item['label']} "
                    "Do not inspect the pipeline source at runtime. Return the packaged playbook, "
                    "preset, schema lookup, output/QC asset, or explicit scoped-out reason that "
                    "handles it."
                ),
                "expected_output": (
                    "A coverage answer grounded in packaged assets. It should either point to the "
                    "playbook, preset, schema group, step recipe, artifact contract, or QC rule "
                    "that covers the capability, or explicitly say the capability is scoped out "
                    "with a reason."
                ),
                "assertions": [
                    "Starts from packaged playbooks or presets rather than authoring-time "
                    "inspection.",
                    "Uses schema-index or grouped schema assets for exact mapping when needed.",
                    "Scopes out the mode with a reason if the packaged assets do not support it.",
                    "Does not use nextflow_inspect_pipeline for runtime planning.",
                    "Does not invent unsupported enum values or parameter names.",
                ],
                "files": [],
            }
        )
    return evals


def _diverse_capability_eval_items(capabilities: list[Any]) -> list[dict[str, Any]]:
    candidates = [
        item
        for item in capabilities
        if isinstance(item, dict)
        and item.get("impact") == "high"
        and isinstance(item.get("label"), str)
    ]
    selected: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_kinds: set[str] = set()

    for item in candidates:
        kind = str(item.get("kind") or "unknown")
        capability_id = str(item.get("id") or "")
        if kind in seen_kinds or capability_id in seen_ids:
            continue
        selected.append(item)
        seen_kinds.add(kind)
        seen_ids.add(capability_id)
        if len(selected) == 3:
            return selected

    for item in candidates:
        capability_id = str(item.get("id") or "")
        if capability_id in seen_ids:
            continue
        selected.append(item)
        seen_ids.add(capability_id)
        if len(selected) == 3:
            return selected

    return selected


def _gap_negative_scope_evals(
    *,
    pipeline_id: str,
    display_name: str,
    authoring_gaps: dict[str, Any],
    covered_gap_ids: set[str],
) -> list[dict[str, Any]]:
    gaps = authoring_gaps.get("gaps")
    if not isinstance(gaps, list):
        return []
    open_gaps = _diverse_open_gap_eval_items(gaps, covered_gap_ids=covered_gap_ids)
    evals = []
    for item in open_gaps:
        gap_id = item["id"]
        gap_source = str(item.get("source") or "assets/authoring-gaps.yaml")
        gap_action = str(item.get("action") or "Review the gap before launch.")
        evals.append(
            {
                "id": f"negative-scope-{_slug(gap_id)}",
                "source": "audit",
                "category": "negative_scope",
                "source_materials": sorted({"assets/authoring-gaps.yaml", gap_source}),
                "prompt": (
                    f"Using the {pipeline_id}-expert-skill, answer a {display_name} user whose "
                    f"request depends on unresolved authoring gap `{gap_id}` from `{gap_source}`. "
                    f"The authoring action says: {gap_action} Do not pretend the skill has "
                    "complete source-backed coverage. Return the safest planning answer and say "
                    "what must be reviewed or scoped out before launch."
                ),
                "expected_output": (
                    "A cautious answer that checks authoring-gaps.yaml, avoids pretending the gap "
                    "is covered, and either asks for source-backed review or states the limitation "
                    "before any launch recommendation."
                ),
                "assertions": [
                    "Mentions authoring-gaps.yaml or an unresolved gap.",
                    "Scopes out the mode with a reason if the packaged assets do not support it.",
                    "Does not use nextflow_inspect_pipeline for runtime planning.",
                    "Does not invent unsupported enum values or parameter names.",
                ],
                "files": [],
            }
        )
    return evals


def _diverse_open_gap_eval_items(
    gaps: list[Any], *, covered_gap_ids: set[str]
) -> list[dict[str, Any]]:
    open_gaps = [
        item
        for item in gaps
        if isinstance(item, dict)
        and item.get("status") == "open"
        and isinstance(item.get("id"), str)
        and item["id"] not in covered_gap_ids
    ]
    selected: list[dict[str, Any]] = []
    seen_sources: set[str] = set()

    for item in open_gaps:
        source = str(item.get("source") or "unknown")
        if source in seen_sources:
            continue
        selected.append(item)
        seen_sources.add(source)
        if len(selected) == 3:
            return selected

    for item in open_gaps:
        if item in selected:
            continue
        selected.append(item)
        if len(selected) == 3:
            return selected

    return selected


def _evidence_materials(evidence: Any) -> list[str]:
    materials: list[str] = []
    if not isinstance(evidence, list):
        return materials
    for item in evidence:
        if not isinstance(item, dict):
            continue
        source = item.get("source")
        path = item.get("path")
        if isinstance(source, str) and isinstance(path, str):
            if source == "schema":
                materials.append("authoring_bundle.schema")
            else:
                materials.append(f"authoring_bundle.{source}:{path}")
    return materials


def _humanize_identifier(value: str) -> str:
    return " ".join(part.capitalize() for part in value.replace("-", "_").split("_") if part)


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unknown"


def _require_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise ValueError(f"Expected non-empty string for {key}")


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a minimal editable pipeline expert skill from an authoring bundle."
    )
    parser.add_argument(
        "--bundle", required=True, help="Path to an inspect-style authoring bundle JSON file."
    )
    parser.add_argument(
        "--output-root",
        required=True,
        help=(
            "Output directory for the expert skill scaffold. Its basename must be "
            "<pipeline>-expert-skill."
        ),
    )
    parser.add_argument(
        "--pipeline-version",
        default="unknown",
        help="Pipeline version string for frontmatter and pipeline-profile.yaml.",
    )
    parser.add_argument(
        "--schema-group-overrides",
        help="Optional YAML file with schema group overrides passed to generate_schema_groups.py.",
    )
    args = parser.parse_args()

    bundle = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
    if not isinstance(bundle, dict):
        raise ValueError("authoring bundle JSON must parse to an object")
    overrides = None
    if args.schema_group_overrides:
        overrides = yaml.safe_load(Path(args.schema_group_overrides).read_text(encoding="utf-8"))
        if overrides is not None and not isinstance(overrides, dict):
            raise ValueError("schema group overrides YAML must parse to a mapping")

    scaffold_expert_skill(
        bundle,
        output_root=Path(args.output_root),
        pipeline_version=args.pipeline_version,
        schema_group_overrides=overrides,
    )
    print(f"Scaffolded expert skill at {Path(args.output_root).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
