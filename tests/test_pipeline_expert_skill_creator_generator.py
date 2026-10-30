from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from types import ModuleType

import yaml

from nextmcp.nextflow_catalog import build_pipeline_inspect_payload, load_local_pipeline
from nextmcp.nextflow_schema import flatten_nextflow_schema

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = (
    REPO_ROOT
    / "skills"
    / "meta"
    / "pipeline-expert-skill-creator"
    / "scripts"
    / "generate_schema_groups.py"
)
AUTHORING_BUNDLE_PATH = (
    REPO_ROOT
    / "skills"
    / "meta"
    / "pipeline-expert-skill-creator"
    / "scripts"
    / "build_authoring_bundle.py"
)
SCAFFOLD_PATH = (
    REPO_ROOT
    / "skills"
    / "meta"
    / "pipeline-expert-skill-creator"
    / "scripts"
    / "scaffold_expert_skill.py"
)
AUDIT_PATH = (
    REPO_ROOT
    / "skills"
    / "meta"
    / "pipeline-expert-skill-creator"
    / "scripts"
    / "audit_capabilities.py"
)
VALIDATOR_PATH = (
    REPO_ROOT
    / "skills"
    / "meta"
    / "pipeline-expert-skill-creator"
    / "scripts"
    / "validate_expert_skill.py"
)
OFFLINE_EVAL_RUNNER_PATH = (
    REPO_ROOT
    / "skills"
    / "meta"
    / "pipeline-expert-skill-creator"
    / "scripts"
    / "run_offline_evals.py"
)
EVAL_TEMPLATE_PATH = (
    REPO_ROOT
    / "skills"
    / "meta"
    / "pipeline-expert-skill-creator"
    / "evals"
    / "templates"
    / "expert-skill-evals.json"
)


def _load_generator_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "pipeline_expert_skill_creator_generator", GENERATOR_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_offline_eval_runner_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "pipeline_expert_skill_creator_offline_eval_runner", OFFLINE_EVAL_RUNNER_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_scaffold_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "pipeline_expert_skill_creator_scaffold", SCAFFOLD_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_authoring_bundle_script_matches_inspect_materials_shape(tmp_path: Path) -> None:
    pipeline_dir = tmp_path / "rnaseq"
    pipeline_dir.mkdir()
    (pipeline_dir / "main.nf").write_text("workflow {}\n", encoding="utf-8")
    (pipeline_dir / "nextflow.config").write_text("params.outdir = 'results'\n", encoding="utf-8")
    (pipeline_dir / "interactive.nf").write_text("workflow {}\n", encoding="utf-8")
    (pipeline_dir / "README.md").write_text("# RNA-seq\n", encoding="utf-8")
    docs_dir = pipeline_dir / "docs"
    docs_dir.mkdir()
    (docs_dir / "usage.md").write_text("Usage\n", encoding="utf-8")
    workflows_dir = pipeline_dir / "workflows"
    workflows_dir.mkdir()
    (workflows_dir / "rnaseq.nf").write_text("workflow {}\n", encoding="utf-8")
    schema = {
        "title": "RNA-seq test pipeline",
        "description": "Demo pipeline for authoring bundle tests.",
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "format": "file-path",
                "description": "Input samplesheet.",
            }
        },
        "required": ["input"],
    }
    (pipeline_dir / "nextflow_schema.json").write_text(json.dumps(schema), encoding="utf-8")

    expected = build_pipeline_inspect_payload(load_local_pipeline(pipeline_dir), detail="materials")
    output_path = tmp_path / "bundle.json"
    subprocess.run(
        [
            "python",
            str(AUTHORING_BUNDLE_PATH),
            "--pipeline",
            str(pipeline_dir),
            "--output",
            str(output_path),
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    actual = json.loads(output_path.read_text(encoding="utf-8"))
    assert actual == expected


def test_offline_eval_template_has_expected_categories() -> None:
    payload = json.loads(EVAL_TEMPLATE_PATH.read_text(encoding="utf-8"))

    assert payload["template_name"] == "pipeline-expert-skill-offline-evals"
    assert payload["template_version"] == "v2"
    assert payload["usage"]["run_mode"] == "offline"
    assert payload["usage"]["nextflow_launch_required"] is False

    evals = payload["evals"]
    assert {item["category"] for item in evals} == {
        "parameter_mapping",
        "route_selection",
        "outputs_qc",
        "historical_reuse",
        "coverage",
        "negative_scope",
    }
    assert {"asset", "authoring_bundle", "audit"}.issubset({item["source"] for item in evals})
    for item in evals:
        assert item["id"]
        assert item["source"]
        assert item["source_materials"]
        assert item["prompt"]
        assert item["expected_output"]
        assert item["assertions"]
        assert item["files"] == []


def test_scaffold_expert_skill_script_writes_minimal_editable_package(tmp_path: Path) -> None:
    pipeline_dir = tmp_path / "rnaseq"
    pipeline_dir.mkdir()
    (pipeline_dir / "main.nf").write_text("workflow {}\n", encoding="utf-8")
    (pipeline_dir / "nextflow.config").write_text("params.outdir = 'results'\n", encoding="utf-8")
    (pipeline_dir / "interactive.nf").write_text("workflow {}\n", encoding="utf-8")
    (pipeline_dir / "README.md").write_text("# RNA-seq\n", encoding="utf-8")
    docs_dir = pipeline_dir / "docs"
    docs_dir.mkdir()
    (docs_dir / "usage.md").write_text("Usage\n", encoding="utf-8")
    workflows_dir = pipeline_dir / "workflows"
    workflows_dir.mkdir()
    (workflows_dir / "rnaseq.nf").write_text("workflow {}\n", encoding="utf-8")
    schema = {
        "title": "RNA-seq test pipeline",
        "description": "Demo pipeline for scaffold tests.",
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "format": "file-path",
                "description": "Input samplesheet.",
            },
            "outdir": {
                "type": "string",
                "format": "directory-path",
                "description": "Output directory.",
            },
        },
        "required": ["input"],
    }
    (pipeline_dir / "nextflow_schema.json").write_text(json.dumps(schema), encoding="utf-8")

    bundle = build_pipeline_inspect_payload(load_local_pipeline(pipeline_dir), detail="materials")
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    output_root = tmp_path / "rnaseq-expert-skill"

    subprocess.run(
        [
            "python",
            str(SCAFFOLD_PATH),
            "--bundle",
            str(bundle_path),
            "--output-root",
            str(output_root),
            "--pipeline-version",
            "0.1.0",
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    required_paths = (
        "SKILL.md",
        "assets/pipeline-profile.yaml",
        "assets/playbooks.yaml",
        "assets/capability-audit.yaml",
        "assets/authoring-gaps.yaml",
        "assets/step-recipes.yaml",
        "assets/param-presets.yaml",
        "assets/schema-index.yaml",
        "assets/artifact-contracts.yaml",
        "assets/qc-rules.yaml",
        "references/01_scope_and_assumptions.md",
        "references/02_playbooks.md",
        "references/03_parameters.md",
        "references/04_schema_lookup.md",
        "references/05_outputs_and_qc.md",
        "references/06_troubleshooting.md",
        "references/schema-groups/input_paths_and_manifests.md",
        "assets/schema-groups/input_paths_and_manifests.yaml",
        "evals/evals.json",
    )
    for relative_path in required_paths:
        assert (output_root / relative_path).is_file(), relative_path

    frontmatter_text = (output_root / "SKILL.md").read_text(encoding="utf-8")
    assert "name: rnaseq-expert-skill" in frontmatter_text
    assert (
        "Read first when deciding whether this skill covers the user's request." in frontmatter_text
    )
    assert "Read only the group named by `schema-index.yaml`." in frontmatter_text
    assert "Read before preparing a launch plan." in frontmatter_text
    assert "## Fast-start playbooks" in frontmatter_text

    pipeline_profile = yaml.safe_load(
        (output_root / "assets" / "pipeline-profile.yaml").read_text(encoding="utf-8")
    )
    assert pipeline_profile["pipeline"]["id"] == "rnaseq"
    assert pipeline_profile["pipeline"]["version"] == "0.1.0"

    presets = yaml.safe_load(
        (output_root / "assets" / "param-presets.yaml").read_text(encoding="utf-8")
    )
    assert "default_run" in presets["presets"]

    capability_audit = yaml.safe_load(
        (output_root / "assets" / "capability-audit.yaml").read_text(encoding="utf-8")
    )
    assert capability_audit["pipeline_id"] == "rnaseq"
    assert capability_audit["capabilities"]

    authoring_gaps = yaml.safe_load(
        (output_root / "assets" / "authoring-gaps.yaml").read_text(encoding="utf-8")
    )
    assert authoring_gaps["status"] == "open"
    assert authoring_gaps["gaps"]

    evals_payload = json.loads((output_root / "evals" / "evals.json").read_text(encoding="utf-8"))
    assert evals_payload["template_version"] == "v2"
    eval_sources = {item["source"] for item in evals_payload["evals"]}
    assert {"asset", "authoring_bundle", "audit"}.issubset(eval_sources)
    assert any(item["category"] == "coverage" for item in evals_payload["evals"])
    assert any(item["category"] == "negative_scope" for item in evals_payload["evals"])
    for item in evals_payload["evals"]:
        assert item["source_materials"]


def test_scaffold_offline_evals_pick_diverse_capabilities_and_gaps() -> None:
    module = _load_scaffold_module()
    capability_audit = {
        "capabilities": [
            {
                "id": "documented_prerequisite_database",
                "label": "Documented `database` prerequisite should be explicit in planning.",
                "kind": "runtime_prerequisite",
                "impact": "high",
                "required_assets": ["playbooks.yaml"],
                "evidence": [{"source": "documents", "path": "README.md", "excerpt": "database"}],
            },
            {
                "id": "documented_prerequisite_index",
                "label": "Documented `index` prerequisite should be explicit in planning.",
                "kind": "runtime_prerequisite",
                "impact": "high",
                "required_assets": ["playbooks.yaml"],
                "evidence": [{"source": "documents", "path": "README.md", "excerpt": "index"}],
            },
            {
                "id": "schema_param_aligner",
                "label": "Schema parameter `aligner` may change run planning.",
                "kind": "schema_parameter",
                "impact": "high",
                "required_assets": ["param-presets.yaml"],
                "evidence": [
                    {
                        "source": "schema",
                        "path": "nextflow_schema.json",
                        "field": "aligner",
                    }
                ],
            },
            {
                "id": "step_entry_STEP_BUILD_STAR_INDEX",
                "label": "Step workflow `STEP_BUILD_STAR_INDEX` should be covered.",
                "kind": "step_entry",
                "impact": "high",
                "required_assets": ["step-recipes.yaml"],
                "evidence": [
                    {
                        "source": "source_files",
                        "path": "workflows/rnaseq.nf",
                        "excerpt": "STEP_BUILD_STAR_INDEX",
                    }
                ],
            },
        ]
    }
    authoring_gaps = {
        "gaps": [
            {
                "id": "documented_prerequisite_database",
                "source": "capability-audit.yaml",
                "status": "open",
                "action": "Cover this prerequisite.",
            },
            {
                "id": "documented_prerequisite_index",
                "source": "capability-audit.yaml",
                "status": "open",
                "action": "Cover this prerequisite.",
            },
            {
                "id": "schema_param_aligner",
                "source": "capability-audit.yaml",
                "status": "open",
                "action": "Cover this parameter.",
            },
            {
                "id": "step_entry_STEP_BUILD_STAR_INDEX",
                "source": "capability-audit.yaml",
                "status": "open",
                "action": "Cover this step entry.",
            },
            {
                "id": "replace_generic_artifact_contract",
                "source": "artifact-contracts.yaml",
                "status": "open",
                "action": "Replace the generic artifact contract.",
            },
        ]
    }

    payload = module._offline_evals(
        pipeline_id="rnaseq",
        display_name="nf-core/rnaseq",
        required_inputs=[],
        capability_audit=capability_audit,
        authoring_gaps=authoring_gaps,
    )

    coverage_ids = [item["id"] for item in payload["evals"] if item["category"] == "coverage"]
    negative_ids = [item["id"] for item in payload["evals"] if item["category"] == "negative_scope"]

    assert "source-coverage-documented-prerequisite-database" in coverage_ids
    assert "source-coverage-schema-param-aligner" in coverage_ids
    assert "source-coverage-step-entry-step-build-star-index" in coverage_ids
    assert "source-coverage-documented-prerequisite-index" not in coverage_ids
    assert "negative-scope-documented-prerequisite-index" in negative_ids
    assert "negative-scope-documented-prerequisite-database" not in negative_ids
    assert len({item["prompt"] for item in payload["evals"]}) == len(payload["evals"])


def test_schema_group_generator_preserves_grouped_schema_parameters(tmp_path: Path) -> None:
    module = _load_generator_module()
    schema = {
        "title": "Grouped generator example",
        "type": "object",
        "$defs": {
            "input_options": {
                "title": "Input options",
                "type": "object",
                "required": ["input"],
                "properties": {
                    "input": {"type": "string", "format": "file-path"},
                    "outdir": {"type": "string", "default": "results"},
                },
            },
            "alignment_options": {
                "title": "Alignment options",
                "type": "object",
                "properties": {
                    "aligner": {"type": "string", "enum": ["star", "hisat2"]},
                    "save_intermediates": {"type": "boolean", "default": False},
                },
            },
        },
        "allOf": [
            {"$ref": "#/$defs/input_options"},
            {"$ref": "#/$defs/alignment_options"},
        ],
    }
    assert isinstance(schema, dict)
    defs = schema.get("$defs") or schema.get("definitions")
    assert isinstance(defs, dict)
    all_of = schema.get("allOf")
    assert isinstance(all_of, list)

    artifacts = module.generate_schema_group_artifacts(
        schema,
        pipeline_id="rnaseq",
        overrides=None,
        write_reference_drafts=True,
    )
    module.write_schema_group_artifacts(
        output_root=tmp_path,
        schema_index=artifacts["schema_index"],
        group_payloads=artifacts["group_payloads"],
        reference_drafts=artifacts["reference_drafts"],
    )

    flattened = flatten_nextflow_schema(schema)
    schema_index = yaml.safe_load(
        (tmp_path / "assets" / "schema-index.yaml").read_text(encoding="utf-8")
    )
    assert schema_index["grouping_strategy"]

    collected_params: set[str] = set()
    group_ids = [group["id"] for group in schema_index["groups"]]
    expected_group_ids = [
        item["$ref"].split("/")[-1]
        for item in all_of
        if isinstance(item, dict) and isinstance(item.get("$ref"), str)
    ]
    assert group_ids == expected_group_ids

    for group in schema_index["groups"]:
        asset_path = tmp_path / group["asset_path"]
        reference_path = tmp_path / group["reference_path"]
        assert asset_path.is_file()
        assert reference_path.is_file()

        payload = yaml.safe_load(asset_path.read_text(encoding="utf-8"))
        assert payload["group"]["id"] == group["id"]
        assert payload["group"]["selection_rule"]
        assert payload["group"]["lookup_order"]
        assert payload["group"]["coverage_notes"]
        assert group["label"] == defs[group["id"]]["title"]

        params = payload["parameters"]
        assert group["summary"] == payload["group"]["coverage_notes"]
        assert group["parameter_count"] == len(params)
        for param in params:
            collected_params.add(param["name"])
            assert param["group_id"] == group["id"]
            assert param["source_name"] == param["name"]
            assert param["classification"] in {"route_shaping", "lookup_only", "non_runtime"}
            assert param["channel"] in {
                "params",
                "config_files",
                "runtime_metadata",
                "authoring_only",
            }
            assert "mapping_notes" in param
            assert "lookup_priority" in param
            assert param["confidence"] in {"low", "medium", "high"}
            assert isinstance(param["mapping_flags"], list)
            assert "raw_schema" in param

    assert collected_params == set(flattened.properties)


def test_schema_group_generator_honors_pipeline_specific_overrides() -> None:
    module = _load_generator_module()
    schema = {
        "type": "object",
        "$defs": {
            "input_output_options": {
                "title": "Input/output options",
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "format": "file-path",
                        "description": "Path to the input samplesheet.",
                    },
                },
                "required": ["input"],
            },
            "alignment_options": {
                "title": "Alignment options",
                "type": "object",
                "properties": {
                    "special_threshold": {
                        "type": "integer",
                        "description": "Threshold controlling a special workflow branch.",
                    },
                },
            },
            "max_job_request_options": {
                "title": "Max job request options",
                "type": "object",
                "properties": {
                    "max_cpus": {
                        "type": "integer",
                        "default": 16,
                        "description": "Maximum available CPUs.",
                    },
                },
            },
        },
        "allOf": [
            {"$ref": "#/$defs/input_output_options"},
            {"$ref": "#/$defs/alignment_options"},
            {"$ref": "#/$defs/max_job_request_options"},
        ],
    }
    overrides = {
        "grouping_strategy": "custom override strategy for tests",
        "parameter_overrides": {
            "special_threshold": {
                "group_id": "alignment_options",
                "classification": "route_shaping",
                "mapping_notes": "Treat as a route-shaping threshold in tests.",
            },
            "input": {
                "placeholder": "<server_input_root>/custom_samplesheet.csv",
            },
        },
    }

    artifacts = module.generate_schema_group_artifacts(
        schema,
        pipeline_id="demo",
        overrides=overrides,
        write_reference_drafts=False,
    )
    schema_index = artifacts["schema_index"]
    assert schema_index["grouping_strategy"] == "custom override strategy for tests"

    route_group = artifacts["group_payloads"]["alignment_options"]["parameters"]
    route_names = [param["name"] for param in route_group]
    assert "special_threshold" in route_names

    input_group = artifacts["group_payloads"]["input_output_options"]["parameters"]
    input_param = next(param for param in input_group if param["name"] == "input")
    assert input_param["placeholder"] == "<server_input_root>/custom_samplesheet.csv"

    tuning_group = artifacts["group_payloads"]["max_job_request_options"]["parameters"]
    max_cpus = next(param for param in tuning_group if param["name"] == "max_cpus")
    assert max_cpus["channel"] == "config_files"


def test_schema_group_generator_falls_back_to_heuristics_without_top_level_sections() -> None:
    module = _load_generator_module()
    schema = {
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "format": "file-path",
                "description": "Path to the input samplesheet.",
            },
            "reference_fasta": {
                "type": "string",
                "format": "file-path",
                "description": "Reference genome FASTA.",
            },
        },
        "required": ["input"],
    }

    artifacts = module.generate_schema_group_artifacts(
        schema,
        pipeline_id="demo",
        overrides=None,
        write_reference_drafts=False,
    )

    schema_index = artifacts["schema_index"]
    assert "heuristic" in schema_index["grouping_strategy"]
    assert "input_paths_and_manifests" in artifacts["group_payloads"]
    assert "references_and_indices" in artifacts["group_payloads"]


def test_schema_group_generator_flags_complex_parameters_for_exact_lookup() -> None:
    module = _load_generator_module()
    schema = {
        "type": "object",
        "properties": {
            "contrasts": {
                "type": "array",
                "description": "Structured contrast definitions.",
                "items": {"type": "object"},
            },
            "mode": {
                "oneOf": [{"const": "fast"}, {"const": "full"}],
                "description": "Mode choice.",
            },
        },
    }

    artifacts = module.generate_schema_group_artifacts(
        schema,
        pipeline_id="demo",
        overrides=None,
        write_reference_drafts=False,
    )
    all_params = [
        param for payload in artifacts["group_payloads"].values() for param in payload["parameters"]
    ]
    contrasts = next(param for param in all_params if param["name"] == "contrasts")
    mode = next(param for param in all_params if param["name"] == "mode")

    assert contrasts["confidence"] == "low"
    assert "needs_exact_lookup" in contrasts["mapping_flags"]
    assert mode["confidence"] == "low"
    assert "uses_oneOf" in mode["mapping_flags"]


def test_capability_audit_script_finds_schema_entries_and_step_outputs(tmp_path: Path) -> None:
    bundle = {
        "pipeline_id": "demo",
        "schema": {
            "type": "object",
            "properties": {
                "with_umi": {
                    "type": "boolean",
                    "description": "Enable UMI extraction.",
                },
                "sentieon_license": {
                    "type": "string",
                    "description": "Sentieon license secret.",
                },
            },
        },
        "source_files": [
            {
                "role": "entry_script",
                "path": "interactive.nf",
                "content": "workflow STEP_BUILD_STAR_INDEX { publishDir 'results' }\n",
            }
        ],
        "documents": [
            {
                "role": "doc",
                "path": "docs/output.md",
                "content": "Review MultiQC reports and BAM files.",
            }
        ],
    }
    bundle_path = tmp_path / "bundle.json"
    output_path = tmp_path / "audit.yaml"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")

    subprocess.run(
        [
            "python",
            str(AUDIT_PATH),
            "--bundle",
            str(bundle_path),
            "--output",
            str(output_path),
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    audit = yaml.safe_load(output_path.read_text(encoding="utf-8"))
    capability_ids = {item["id"] for item in audit["capabilities"]}
    assert audit["status"] == "needs_review"
    assert "schema_param_with_umi" in capability_ids
    assert "prerequisite_sentieon_license" in capability_ids
    assert "alternate_entry_interactive_nf" in capability_ids
    assert "step_entry_step_build_star_index" in capability_ids
    assert "documented_output_multiqc" in capability_ids


def test_validate_expert_skill_script_fails_open_scaffold_gaps(tmp_path: Path) -> None:
    pipeline_dir = tmp_path / "rnaseq"
    pipeline_dir.mkdir()
    (pipeline_dir / "main.nf").write_text("workflow {}\n", encoding="utf-8")
    (pipeline_dir / "README.md").write_text("# RNA-seq\n", encoding="utf-8")
    schema = {
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "format": "file-path",
                "description": "Input samplesheet.",
            },
        },
        "required": ["input"],
    }
    (pipeline_dir / "nextflow_schema.json").write_text(json.dumps(schema), encoding="utf-8")
    bundle = build_pipeline_inspect_payload(load_local_pipeline(pipeline_dir), detail="materials")
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    output_root = tmp_path / "rnaseq-expert-skill"
    report_path = tmp_path / "validation.json"

    subprocess.run(
        [
            "python",
            str(SCAFFOLD_PATH),
            "--bundle",
            str(bundle_path),
            "--output-root",
            str(output_root),
        ],
        check=True,
        cwd=REPO_ROOT,
    )
    result = subprocess.run(
        [
            "python",
            str(VALIDATOR_PATH),
            "--skill-root",
            str(output_root),
            "--bundle",
            str(bundle_path),
            "--json-output",
            str(report_path),
        ],
        check=False,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 1
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["status"] == "fail"
    failed_ids = {check["id"] for check in report["checks"] if check["status"] == "fail"}
    assert "authoring-gaps" in failed_ids


def test_run_offline_evals_script_writes_outputs_with_mock_agent(tmp_path: Path) -> None:
    skill_root = tmp_path / "demo-expert-skill"
    evals_dir = skill_root / "evals"
    evals_dir.mkdir(parents=True)
    (skill_root / "SKILL.md").write_text(
        "---\nname: demo-expert-skill\n---\n# Demo\n",
        encoding="utf-8",
    )
    evals_payload = {
        "evals": [
            {
                "id": "parameter-channel-mapping",
                "source": "asset",
                "category": "parameter_mapping",
                "source_materials": ["assets/param-presets.yaml"],
                "prompt": "Draft a dry launch plan.",
                "expected_output": "Project is top-level and params hold input.",
                "assertions": [
                    "Mentions project as a top-level nextflow_run argument, not inside params.",
                    "Mentions input and outdir under params.",
                ],
                "files": [],
            }
        ]
    }
    (evals_dir / "evals.json").write_text(json.dumps(evals_payload), encoding="utf-8")
    workspace = tmp_path / "workspace"

    subprocess.run(
        [
            "python",
            str(OFFLINE_EVAL_RUNNER_PATH),
            "--skill-root",
            str(skill_root),
            "--workspace",
            str(workspace),
            "--agent",
            "mock",
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    iteration_root = workspace / "iteration-1"
    summary = json.loads((iteration_root / "summary.json").read_text(encoding="utf-8"))
    grading = json.loads(
        (iteration_root / "parameter-channel-mapping" / "with_skill" / "grading.json").read_text(
            encoding="utf-8"
        )
    )

    assert summary["summary"]["eval_count"] == 1
    assert summary["summary"]["passed"] == 1
    assert summary["summary"]["by_source"]["asset"]["passed"] == 1
    assert summary["summary"]["by_category"]["parameter_mapping"]["passed"] == 1
    assert summary["runs"][0]["source"] == "asset"
    assert summary["runs"][0]["category"] == "parameter_mapping"
    assert grading["passed"] is True
    assert (
        iteration_root / "parameter-channel-mapping" / "with_skill" / "outputs" / "response.md"
    ).is_file()


def test_run_offline_evals_agent_prompt_hides_expected_output_and_assertions() -> None:
    module = _load_offline_eval_runner_module()
    prompt = module._build_agent_prompt(
        skill_root=REPO_ROOT / "skills" / "experts" / "demo-expert-skill",
        eval_case={
            "prompt": "Draft a dry launch plan.",
            "expected_output": "Secret expected answer.",
            "assertions": ["Secret assertion."],
        },
    )

    assert "Draft a dry launch plan." in prompt
    assert "Write the entire eval response in English" in prompt
    assert "Secret expected answer." not in prompt
    assert "Secret assertion." not in prompt
    assert "Expected output:" not in prompt
    assert "Assertions to satisfy:" not in prompt


def test_run_offline_evals_grader_allows_negated_inspect_tool_mentions() -> None:
    module = _load_offline_eval_runner_module()

    passed, _ = module._grade_assertion(
        output="Do not call `nextflow_inspect_pipeline`; use packaged assets first.",
        assertion="Does not use nextflow_inspect_pipeline for runtime planning.",
        dry_run=False,
    )

    assert passed is True


def test_run_offline_evals_grader_rejects_positive_inspect_tool_use() -> None:
    module = _load_offline_eval_runner_module()

    passed, _ = module._grade_assertion(
        output="Verify publishDir paths via nextflow_inspect_pipeline before planning.",
        assertion="Does not use nextflow_inspect_pipeline for runtime planning.",
        dry_run=False,
    )

    assert passed is False


def test_run_offline_evals_grader_allows_forbidden_inspect_tool_list() -> None:
    module = _load_offline_eval_runner_module()

    passed, _ = module._grade_assertion(
        output=(
            "forbidden_fallbacks:\n"
            "  - nextflow_inspect_pipeline as a runtime planning step.\n"
            "  - Source-tree publishDir review as a runtime fallback.\n"
        ),
        assertion="Does not use nextflow_inspect_pipeline for runtime planning.",
        dry_run=False,
    )

    assert passed is True


def test_run_offline_evals_grader_accepts_summary_before_logs() -> None:
    module = _load_offline_eval_runner_module()

    passed, _ = module._grade_assertion(
        output=(
            'Start with run_get(include=["progress","artifact_summary","diagnosis",'
            '"next_actions"]), then use run_artifacts. Inspect run_artifacts before raw logs.'
        ),
        assertion="Does not jump straight to raw logs as the default first step.",
        dry_run=False,
    )

    assert passed is True


def test_run_offline_evals_grader_allows_scoped_out_schema_lookup() -> None:
    module = _load_offline_eval_runner_module()

    passed, _ = module._grade_assertion(
        output=(
            "verdict: scoped_out\n"
            "scope_out_reason: The pipeline has no standalone index runtime prerequisite. "
            "No runtime planning action is required."
        ),
        assertion="Uses schema-index or grouped schema assets for exact mapping when needed.",
        dry_run=False,
    )

    assert passed is True


def test_run_offline_evals_supports_kimi_agent_command(tmp_path: Path) -> None:
    module = _load_offline_eval_runner_module()
    skill_root = tmp_path / "skills" / "experts" / "demo-expert-skill"
    skill_root.mkdir(parents=True)

    command = module._agent_command(
        agent="kimi",
        prompt="Plan a dry run.",
        skill_root=skill_root,
    )

    assert command[0] == "kimi"
    assert "--quiet" in command
    assert "--prompt" in command
    assert "Plan a dry run." in command
    assert "--skills-dir" in command
    assert str(skill_root.parent) in command


def test_offline_codex_command_pins_model_and_read_only_sandbox() -> None:
    module = _load_offline_eval_runner_module()
    command = module._agent_command(
        agent="codex",
        prompt="Plan only.",
        skill_root=REPO_ROOT / "skills" / "experts" / "rnaseq-expert-skill",
        model="gpt-6-astra",
    )
    assert command[command.index("--model") + 1] == "gpt-6-astra"
    assert command[command.index("--sandbox") + 1] == "read-only"
    assert command[command.index("--cd") + 1] == str(
        REPO_ROOT / "skills" / "experts" / "rnaseq-expert-skill"
    )
    assert command.index("--ask-for-approval") < command.index("exec")
    assert "--skip-git-repo-check" in command
    assert "--ephemeral" in command


def test_offline_pass_is_not_reused_after_model_or_skill_changes(tmp_path: Path) -> None:
    module = _load_offline_eval_runner_module()
    run_dir = tmp_path / "case" / "with_skill"
    run_dir.mkdir(parents=True)
    (run_dir / "grading.json").write_text('{"passed": true}', encoding="utf-8")
    metadata = {"agent": "codex", "model": "old-model", "skill_sha256": "old-skill"}
    module._write_json(run_dir.parent / "eval_metadata.json", metadata)
    for change in ({"model": "new-model"}, {"skill_sha256": "new-skill"}):
        result = module._passed_existing_run_report(
            run_dir=run_dir,
            metadata={**metadata, **change},
            eval_name="case",
            progress=False,
            progress_label="test",
        )
        assert result is None
