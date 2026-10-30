"""Repository-side skill source package validation tests."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")
FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.DOTALL)

EXPECTED_SKILLS = {
    "experts/ampliseq-expert-skill": {
        "skill_class": "expert",
        "required_paths": [
            "SKILL.md",
            "assets/pipeline-profile.yaml",
            "assets/playbooks.yaml",
            "assets/step-recipes.yaml",
            "assets/param-presets.yaml",
            "assets/artifact-contracts.yaml",
            "assets/qc-rules.yaml",
            "references/01_scope_and_assumptions.md",
            "references/02_playbooks.md",
            "references/03_parameters.md",
            "references/04_schema_lookup.md",
            "references/05_outputs_and_qc.md",
            "references/06_troubleshooting.md",
        ],
    },
    "experts/mag-expert-skill": {
        "skill_class": "expert",
        "required_paths": [
            "SKILL.md",
            "assets/pipeline-profile.yaml",
            "assets/playbooks.yaml",
            "assets/step-recipes.yaml",
            "assets/param-presets.yaml",
            "assets/artifact-contracts.yaml",
            "assets/qc-rules.yaml",
            "references/01_scope_and_assumptions.md",
            "references/02_playbooks.md",
            "references/03_parameters.md",
            "references/04_schema_lookup.md",
            "references/05_outputs_and_qc.md",
            "references/06_troubleshooting.md",
        ],
    },
    "experts/methylseq-expert-skill": {
        "skill_class": "expert",
        "required_paths": [
            "SKILL.md",
            "assets/pipeline-profile.yaml",
            "assets/playbooks.yaml",
            "assets/step-recipes.yaml",
            "assets/param-presets.yaml",
            "assets/artifact-contracts.yaml",
            "assets/qc-rules.yaml",
            "references/01_scope_and_assumptions.md",
            "references/02_playbooks.md",
            "references/03_parameters.md",
            "references/04_schema_lookup.md",
            "references/05_outputs_and_qc.md",
            "references/06_troubleshooting.md",
        ],
    },
    "experts/nanoseq-expert-skill": {
        "skill_class": "expert",
        "required_paths": [
            "SKILL.md",
            "assets/pipeline-profile.yaml",
            "assets/playbooks.yaml",
            "assets/step-recipes.yaml",
            "assets/param-presets.yaml",
            "assets/artifact-contracts.yaml",
            "assets/qc-rules.yaml",
            "references/01_scope_and_assumptions.md",
            "references/02_playbooks.md",
            "references/03_parameters.md",
            "references/04_schema_lookup.md",
            "references/05_outputs_and_qc.md",
            "references/06_troubleshooting.md",
        ],
    },
    "experts/rnaseq-expert-skill": {
        "skill_class": "expert",
        "required_paths": [
            "SKILL.md",
            "assets/pipeline-profile.yaml",
            "assets/playbooks.yaml",
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
        ],
    },
    "experts/scrnaseq-expert-skill": {
        "skill_class": "expert",
        "required_paths": [
            "SKILL.md",
            "assets/pipeline-profile.yaml",
            "assets/playbooks.yaml",
            "assets/step-recipes.yaml",
            "assets/param-presets.yaml",
            "assets/artifact-contracts.yaml",
            "assets/qc-rules.yaml",
            "references/01_scope_and_assumptions.md",
            "references/02_playbooks.md",
            "references/03_parameters.md",
            "references/04_schema_lookup.md",
            "references/05_outputs_and_qc.md",
            "references/06_troubleshooting.md",
        ],
    },
    "meta/pipeline-expert-skill-creator": {
        "skill_class": "meta",
        "required_paths": [
            "SKILL.md",
            "assets/extraction-rules.yaml",
            "assets/asset-schema.yaml",
            "assets/schema-grouping-rules.yaml",
            "assets/validation-checklist.yaml",
            "assets/templates/expert-skill-layout.yaml",
            "assets/templates/frontmatter.yaml",
            "assets/templates/schema-group-overrides.example.yaml",
            "evals/templates/expert-skill-evals.json",
            "references/01_source_inventory.md",
            "references/02_extraction_workflow.md",
            "references/03_rendering_rules.md",
            "references/04_validation.md",
            "scripts/build_authoring_bundle.py",
            "scripts/generate_schema_groups.py",
            "scripts/audit_capabilities.py",
            "scripts/scaffold_expert_skill.py",
            "scripts/validate_expert_skill.py",
        ],
    },
    "meta/pipeline-test-config-localizer": {
        "skill_class": "meta",
        "required_paths": [
            "SKILL.md",
            "assets/workflow-rules.yaml",
            "assets/output-contract.yaml",
            "references/01_scope_and_boundaries.md",
            "references/02_localization_workflow.md",
            "references/03_prompt_rendering.md",
        ],
    },
    "meta/pipeline-smoke-evaluator": {
        "skill_class": "meta",
        "required_paths": [
            "SKILL.md",
            "references/01-evidence-bundle.md",
            "references/02-client-evidence-collection-prompt.md",
        ],
    },
}

EXPECTED_METADATA_KEYS = {
    "operator": {"skill-class", "tool-surface", "tool-surface-version"},
    "expert": {"skill-class", "pipeline-id", "pipeline-version", "generated-from"},
    "meta": {"skill-class", "tool-surface", "tool-surface-version", "generated-from"},
}

REQUIRED_SECTION_GROUPS = (
    ("## Scope",),
    ("## What this skill does not handle", "## Non-Scope"),
    ("## Authoritative assets",),
    ("## References to read next", "## References"),
    ("## Operating rules", "## Runtime Rules", "## Runtime Tool Contract"),
)

EXPERT_RUNTIME_TOOL_NAMES = (
    "project_list",
    "project_get",
    "nextflow_run",
    "run_list",
    "run_get",
    "run_artifacts",
    "run_logs",
    "fs_read",
)

REMOVED_TOOL_NAMES = (
    "nextflow_get_schema",
    "nextflow_get_pipeline",
)


def test_repository_skill_source_packages_include_expected_first_wave_packages() -> None:
    discovered = {
        str(path.relative_to(SKILLS_ROOT)).replace("\\", "/") for path in _skill_source_dirs()
    }
    assert discovered.issuperset(EXPECTED_SKILLS)


def test_repository_skill_source_packages_have_required_layout() -> None:
    for relative_path, spec in EXPECTED_SKILLS.items():
        skill_dir = SKILLS_ROOT / relative_path
        assert skill_dir.is_dir(), relative_path
        for required_path in spec["required_paths"]:
            assert (skill_dir / required_path).is_file(), (
                f"Missing {required_path} in {relative_path}"
            )


def test_pipeline_expert_skill_creator_yaml_assets_are_parseable() -> None:
    relative_path = "meta/pipeline-expert-skill-creator"
    skill_dir = SKILLS_ROOT / relative_path
    for required_path in EXPECTED_SKILLS[relative_path]["required_paths"]:
        if not required_path.endswith(".yaml"):
            continue
        payload = yaml.safe_load((skill_dir / required_path).read_text(encoding="utf-8"))
        assert payload is not None, f"Expected YAML payload in {relative_path}/{required_path}"


def test_pipeline_expert_skill_creator_eval_template_is_parseable() -> None:
    template_path = (
        SKILLS_ROOT
        / "meta"
        / "pipeline-expert-skill-creator"
        / "evals"
        / "templates"
        / "expert-skill-evals.json"
    )
    payload = yaml.safe_load(template_path.read_text(encoding="utf-8"))

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


def test_repository_skill_source_packages_have_valid_frontmatter_and_sections() -> None:
    for skill_dir in _skill_source_dirs():
        frontmatter, body = _parse_skill_md(skill_dir / "SKILL.md")

        assert frontmatter["name"] == skill_dir.name
        assert NAME_PATTERN.fullmatch(skill_dir.name)

        description = frontmatter["description"]
        assert isinstance(description, str)
        assert description.strip()

        compatibility = frontmatter.get("compatibility")
        assert isinstance(compatibility, str)
        assert compatibility.strip()

        expected_class = _expected_skill_class(skill_dir)
        metadata = frontmatter["metadata"]
        assert isinstance(metadata, dict)
        assert metadata["skill-class"] == expected_class
        assert EXPECTED_METADATA_KEYS[expected_class].issubset(metadata)
        assert all(isinstance(key, str) for key in metadata)
        assert all(isinstance(value, str) for value in metadata.values())

        body_lower = body.lower()
        for section_titles in REQUIRED_SECTION_GROUPS:
            assert any(section_title.lower() in body_lower for section_title in section_titles), (
                f"Missing one of {section_titles} in {skill_dir}"
            )
        assert re.search(r"^## Fast[- ]start", body, flags=re.IGNORECASE | re.MULTILINE), skill_dir


def test_rnaseq_expert_skill_uses_runtime_tool_names_and_avoids_runtime_inspect() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "rnaseq-expert-skill"
    expert_runtime_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "references" / "02_playbooks.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
    ]
    expert_runtime_content = "\n".join(
        path.read_text(encoding="utf-8") for path in expert_runtime_files
    )
    historical_reuse_content = "\n".join(
        [
            expert_runtime_content,
            (expert_skill_dir / "assets" / "artifact-contracts.yaml").read_text(encoding="utf-8"),
            (expert_skill_dir / "evals" / "evals.json").read_text(encoding="utf-8"),
        ]
    )
    for tool_name in EXPERT_RUNTIME_TOOL_NAMES:
        assert tool_name in expert_runtime_content
    assert "artifacts.json" in historical_reuse_content
    assert "artifact_path_contains" in historical_reuse_content
    assert "pipeline_fingerprint" in historical_reuse_content
    assert (
        "Do not start normal runtime planning with `nextflow_inspect_pipeline`"
        in expert_runtime_content
        or "ordinary runtime planning through `nextflow_inspect_pipeline`" in expert_runtime_content
    )
    assert 'nextflow_inspect_pipeline(detail="materials")' not in expert_runtime_content
    for removed_tool_name in REMOVED_TOOL_NAMES:
        assert removed_tool_name not in expert_runtime_content


def test_atacseq_expert_skill_uses_runtime_tool_names_and_avoids_runtime_inspect() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "atacseq-expert-skill"
    runtime_tool_names = (
        "project_list",
        "project_get",
        "nextflow_run",
        "run_list",
        "run_get",
        "run_artifacts",
        "run_logs",
        "fs_read",
    )
    expert_runtime_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "references" / "02_playbooks.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
    ]
    expert_runtime_content = "\n".join(
        path.read_text(encoding="utf-8") for path in expert_runtime_files
    )
    historical_reuse_content = "\n".join(
        [
            expert_runtime_content,
            (expert_skill_dir / "assets" / "artifact-contracts.yaml").read_text(encoding="utf-8"),
            (expert_skill_dir / "evals" / "evals.json").read_text(encoding="utf-8"),
        ]
    )
    for tool_name in runtime_tool_names:
        assert tool_name in expert_runtime_content
    assert "artifacts.json" in historical_reuse_content
    assert "artifact_path_contains" in historical_reuse_content
    assert "pipeline_fingerprint" in historical_reuse_content
    assert "nextflow_inspect_pipeline" in expert_runtime_content
    assert 'nextflow_inspect_pipeline(detail="materials")' not in expert_runtime_content
    for removed_tool_name in REMOVED_TOOL_NAMES:
        assert removed_tool_name not in expert_runtime_content


def test_ampliseq_expert_skill_uses_runtime_tool_names_and_avoids_runtime_inspect() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "ampliseq-expert-skill"
    runtime_tool_names = (
        "project_list",
        "project_get",
        "nextflow_run",
        "run_list",
        "run_get",
        "run_artifacts",
        "run_logs",
        "fs_read",
    )
    expert_runtime_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "references" / "02_playbooks.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
    ]
    expert_runtime_content = "\n".join(
        path.read_text(encoding="utf-8") for path in expert_runtime_files
    )
    for tool_name in runtime_tool_names:
        assert tool_name in expert_runtime_content
    assert "artifacts.json" in expert_runtime_content
    assert "artifact_path_contains" in expert_runtime_content
    assert "pipeline_fingerprint" in expert_runtime_content
    assert "nextflow_inspect_pipeline" in expert_runtime_content
    assert 'nextflow_inspect_pipeline(detail="materials")' not in expert_runtime_content
    for removed_tool_name in REMOVED_TOOL_NAMES:
        assert removed_tool_name not in expert_runtime_content


def test_ampliseq_expert_skill_makes_server_path_boundary_explicit() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "ampliseq-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
        expert_skill_dir / "assets" / "param-presets.yaml",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "references" / "01_scope_and_assumptions.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    assert "nextmcp server filesystem" in content
    assert "client machine" in content or "client-local" in content
    assert "server-local" in content
    assert "<server_input_root>" in content


def test_ampliseq_expert_skill_keeps_route_params_out_of_config_scope() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "ampliseq-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "`FW_primer`",
        "`RV_primer`",
        "`ancombc",
        "`sbdiexport`",
        "nextflow_run(params=...)",
        "nextflow_run(config_files=[...])",
    ):
        assert token in content


def test_rnaseq_expert_skill_makes_server_path_boundary_explicit() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "rnaseq-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
        expert_skill_dir / "assets" / "param-presets.yaml",
        expert_skill_dir / "assets" / "schema-index.yaml",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "references" / "01_scope_and_assumptions.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "04_schema_lookup.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    assert "nextmcp server filesystem" in content
    assert "client machine" in content or "client-local" in content
    assert "server-local" in content
    assert "<server_input_root>" in content


def test_scrnaseq_expert_skill_uses_runtime_tool_names_and_avoids_runtime_inspect() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "scrnaseq-expert-skill"
    runtime_tool_names = (
        "project_list",
        "project_get",
        "nextflow_run",
        "run_list",
        "run_get",
        "run_artifacts",
        "run_logs",
        "fs_read",
    )
    expert_runtime_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "references" / "02_playbooks.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
    ]
    expert_runtime_content = "\n".join(
        path.read_text(encoding="utf-8") for path in expert_runtime_files
    )
    for tool_name in runtime_tool_names:
        assert tool_name in expert_runtime_content
    assert "artifacts.json" in expert_runtime_content
    assert "artifact_path_contains" in expert_runtime_content
    assert "pipeline_fingerprint" in expert_runtime_content
    assert "authoring-time inspection" in expert_runtime_content or (
        "nextflow_inspect_pipeline" in expert_runtime_content
    )
    assert 'nextflow_inspect_pipeline(detail="materials")' not in expert_runtime_content
    for removed_tool_name in REMOVED_TOOL_NAMES:
        assert removed_tool_name not in expert_runtime_content


def test_scrnaseq_expert_skill_makes_server_path_boundary_explicit() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "scrnaseq-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
        expert_skill_dir / "assets" / "param-presets.yaml",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "references" / "01_scope_and_assumptions.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    assert "nextmcp server filesystem" in content
    assert "client-local" in content or "client machine" in content
    assert "server-local" in content
    assert "<server_input_root>" in content


def test_scrnaseq_expert_skill_covers_significant_optional_modes() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "scrnaseq-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
        expert_skill_dir / "assets" / "playbooks.yaml",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "assets" / "param-presets.yaml",
        expert_skill_dir / "assets" / "artifact-contracts.yaml",
        expert_skill_dir / "assets" / "qc-rules.yaml",
        expert_skill_dir / "references" / "01_scope_and_assumptions.md",
        expert_skill_dir / "references" / "02_playbooks.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "04_schema_lookup.md",
        expert_skill_dir / "references" / "05_outputs_and_qc.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "simpleaf",
        "kallisto",
        "cellranger",
        "cellrangerarc",
        "cellrangermulti",
        "star_feature",
        "kb_workflow",
        "skip_cellbender",
        "cellranger_multi_barcodes",
        "cellrangerarc_config",
        "Gene Velocyto",
        "web_summary.html",
    ):
        assert token in content


def test_ampliseq_expert_skill_covers_significant_optional_modes() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "ampliseq-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
        expert_skill_dir / "assets" / "playbooks.yaml",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "assets" / "param-presets.yaml",
        expert_skill_dir / "assets" / "artifact-contracts.yaml",
        expert_skill_dir / "assets" / "qc-rules.yaml",
        expert_skill_dir / "references" / "01_scope_and_assumptions.md",
        expert_skill_dir / "references" / "02_playbooks.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "04_schema_lookup.md",
        expert_skill_dir / "references" / "05_outputs_and_qc.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
        expert_skill_dir / "assets" / "schema-groups" / "asv_post_processing.yaml",
        expert_skill_dir / "references" / "schema-groups" / "asv_post_processing.md",
        expert_skill_dir / "assets" / "schema-groups" / "taxonomic_assignment.yaml",
        expert_skill_dir / "references" / "schema-groups" / "taxonomic_assignment.md",
        expert_skill_dir / "evals" / "evals.json",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "input_fasta",
        "multiregion",
        "sidle_ref_taxonomy",
        "pplace_tree",
        "classifier",
        "pacbio",
        "iontorrent",
        "illumina_pe_its",
        "multiple_sequencing_runs",
        "vsearch_cluster",
        "filter_ssu",
        "ancombc",
        "classifier.qza",
        "reconstructed_feature-table.tsv",
    ):
        assert token in content


def test_mag_expert_skill_uses_runtime_tool_names_and_avoids_runtime_inspect() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "mag-expert-skill"
    runtime_tool_names = (
        "project_list",
        "project_get",
        "nextflow_run",
        "run_list",
        "run_get",
        "run_artifacts",
        "run_logs",
        "fs_read",
    )
    expert_runtime_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "references" / "02_playbooks.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
    ]
    expert_runtime_content = "\n".join(
        path.read_text(encoding="utf-8") for path in expert_runtime_files
    )
    historical_reuse_content = "\n".join(
        [
            expert_runtime_content,
            (expert_skill_dir / "assets" / "artifact-contracts.yaml").read_text(encoding="utf-8"),
            (expert_skill_dir / "evals" / "evals.json").read_text(encoding="utf-8"),
        ]
    )
    for tool_name in runtime_tool_names:
        assert tool_name in expert_runtime_content
    assert "artifacts.json" in historical_reuse_content
    assert "artifact_path_contains" in historical_reuse_content
    assert "pipeline_fingerprint" in historical_reuse_content
    assert "Do not call `nextflow_inspect_pipeline` during ordinary runtime planning" in (
        expert_runtime_content
    )
    assert 'nextflow_inspect_pipeline(detail="materials")' not in expert_runtime_content
    for removed_tool_name in REMOVED_TOOL_NAMES:
        assert removed_tool_name not in expert_runtime_content


def test_mag_expert_skill_makes_server_path_boundary_explicit() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "mag-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
        expert_skill_dir / "assets" / "param-presets.yaml",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "references" / "01_scope_and_assumptions.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    assert "nextmcp server filesystem" in content
    assert "client-local path" in content
    assert "server-local" in content
    assert "<server_input_root>" in content


def test_mag_expert_skill_explains_conditional_checkm_databases() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "mag-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
        expert_skill_dir / "assets" / "playbooks.yaml",
        expert_skill_dir / "assets" / "param-presets.yaml",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "references" / "01_scope_and_assumptions.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    assert "run_checkm=false" in content
    assert "run_checkm2=false" in content
    assert "Do not block a normal run on `checkm_db` or `checkm2_db`" in content
    assert "checkm_db" in content
    assert "checkm2_db" in content
    assert "default route does not need them" in content


def test_methylseq_expert_skill_uses_runtime_tool_names_and_avoids_runtime_inspect() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "methylseq-expert-skill"
    runtime_tool_names = (
        "project_list",
        "project_get",
        "nextflow_run",
        "run_list",
        "run_get",
        "run_artifacts",
        "run_logs",
        "fs_read",
    )
    expert_runtime_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "references" / "02_playbooks.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
    ]
    expert_runtime_content = "\n".join(
        path.read_text(encoding="utf-8") for path in expert_runtime_files
    )
    historical_reuse_content = "\n".join(
        [
            expert_runtime_content,
            (expert_skill_dir / "assets" / "artifact-contracts.yaml").read_text(encoding="utf-8"),
            (expert_skill_dir / "evals" / "evals.json").read_text(encoding="utf-8"),
        ]
    )
    for tool_name in runtime_tool_names:
        assert tool_name in expert_runtime_content
    assert "artifacts.json" in historical_reuse_content
    assert "artifact_path_contains" in historical_reuse_content
    assert "pipeline_fingerprint" in historical_reuse_content
    assert "nextflow_inspect_pipeline" in expert_runtime_content
    assert 'nextflow_inspect_pipeline(detail="materials")' not in expert_runtime_content
    for removed_tool_name in REMOVED_TOOL_NAMES:
        assert removed_tool_name not in expert_runtime_content


def test_methylseq_expert_skill_makes_server_path_boundary_explicit() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "methylseq-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
        expert_skill_dir / "assets" / "param-presets.yaml",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "references" / "01_scope_and_assumptions.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    assert "nextmcp server filesystem" in content
    assert "client-local" in content or "client machine" in content
    assert "server-local" in content
    assert "<server_input_root>" in content


def test_methylseq_expert_skill_covers_significant_optional_modes() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "methylseq-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
        expert_skill_dir / "assets" / "playbooks.yaml",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "assets" / "param-presets.yaml",
        expert_skill_dir / "assets" / "artifact-contracts.yaml",
        expert_skill_dir / "assets" / "qc-rules.yaml",
        expert_skill_dir / "references" / "01_scope_and_assumptions.md",
        expert_skill_dir / "references" / "02_playbooks.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "04_schema_lookup.md",
        expert_skill_dir / "references" / "05_outputs_and_qc.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "bismark_hisat",
        "known_splices",
        "slamseq",
        "use_mem2",
        "bwameth_gpu",
        "taps_bwamem_rastair",
        "aligner=bwamem",
        "run_targeted_sequencing",
        "collecthsmetrics",
        "rrbs",
        "pbat",
        "single_cell",
        "em_seq",
        "zymo",
        "accel",
        "nomeseq",
        "all_contexts",
        "methyl_kit",
        "targeted.bedGraph",
        "rastair",
    ):
        assert token in content


def test_methylseq_expert_skill_preserves_pipeline_specific_resource_override_shape() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "methylseq-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    _assert_resource_caps_use_config_files(content)


def test_expert_skills_use_from_run_id_as_only_public_restart_route() -> None:
    expert_dirs = [
        SKILLS_ROOT / "experts" / "ampliseq-expert-skill",
        SKILLS_ROOT / "experts" / "mag-expert-skill",
        SKILLS_ROOT / "experts" / "methylseq-expert-skill",
        SKILLS_ROOT / "experts" / "nanoseq-expert-skill",
        SKILLS_ROOT / "experts" / "rnaseq-expert-skill",
        SKILLS_ROOT / "experts" / "scrnaseq-expert-skill",
        SKILLS_ROOT / "experts" / "atacseq-expert-skill",
        SKILLS_ROOT / "experts" / "fetchngs-expert-skill",
        SKILLS_ROOT / "experts" / "riboseq-expert-skill",
        SKILLS_ROOT / "experts" / "sarek-expert-skill",
    ]

    for expert_dir in expert_dirs:
        content = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(expert_dir.rglob("*"))
            if path.is_file() and path.suffix in {".md", ".yaml", ".json"}
        )

        assert "from_run_id" in content, expert_dir
        assert "launch_spec" in content, expert_dir
        assert "nextflow_session_uuid" in content, expert_dir
        assert any(
            token in content
            for token in (
                "resume_compatible",
                "resume compatibility",
                "resume-compatibility",
                "restart compatibility",
                "restart path",
            )
        ), expert_dir
        assert "resume_session_id=" not in content, expert_dir
        assert "resume_session_id:" not in content, expert_dir
        assert "resume=true" not in content, expert_dir


def test_rnaseq_expert_skill_covers_significant_optional_modes() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "rnaseq-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
        expert_skill_dir / "assets" / "playbooks.yaml",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "assets" / "param-presets.yaml",
        expert_skill_dir / "assets" / "schema-index.yaml",
        expert_skill_dir / "assets" / "artifact-contracts.yaml",
        expert_skill_dir / "assets" / "qc-rules.yaml",
        expert_skill_dir / "references" / "01_scope_and_assumptions.md",
        expert_skill_dir / "references" / "02_playbooks.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "04_schema_lookup.md",
        expert_skill_dir / "references" / "05_outputs_and_qc.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
        expert_skill_dir / "evals" / "evals.json",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "with_umi",
        "use_sentieon_star",
        "SENTIEON_LICENSE_BASE64",
        "contaminant_screening",
        "kraken2_bracken",
        "skip_pseudo_alignment",
        "star_index",
        "salmon_index",
        "hisat2_index",
        "rsem_index",
        "stringtie",
    ):
        assert token in content


def test_rnaseq_expert_skill_requires_stopping_on_untrusted_historical_reuse() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "rnaseq-expert-skill"
    checked_files = [
        expert_skill_dir / "assets" / "qc-rules.yaml",
        expert_skill_dir / "references" / "06_troubleshooting.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "pipeline_info/params.json",
        "compare",
        "source run",
        "new launch",
        "do not mix",
    ):
        assert token in content


def test_skill_docs_follow_compact_process_payload_contract() -> None:
    checked_files = [
        SKILLS_ROOT / "experts" / "ampliseq-expert-skill" / "SKILL.md",
        SKILLS_ROOT
        / "experts"
        / "ampliseq-expert-skill"
        / "references"
        / "01_scope_and_assumptions.md",
        SKILLS_ROOT / "experts" / "ampliseq-expert-skill" / "references" / "06_troubleshooting.md",
        SKILLS_ROOT / "experts" / "mag-expert-skill" / "SKILL.md",
        SKILLS_ROOT / "experts" / "mag-expert-skill" / "references" / "01_scope_and_assumptions.md",
        SKILLS_ROOT / "experts" / "mag-expert-skill" / "references" / "06_troubleshooting.md",
        SKILLS_ROOT / "experts" / "nanoseq-expert-skill" / "SKILL.md",
        SKILLS_ROOT
        / "experts"
        / "nanoseq-expert-skill"
        / "references"
        / "01_scope_and_assumptions.md",
        SKILLS_ROOT / "experts" / "nanoseq-expert-skill" / "references" / "06_troubleshooting.md",
        SKILLS_ROOT / "experts" / "rnaseq-expert-skill" / "SKILL.md",
        SKILLS_ROOT
        / "experts"
        / "rnaseq-expert-skill"
        / "references"
        / "01_scope_and_assumptions.md",
        SKILLS_ROOT / "experts" / "rnaseq-expert-skill" / "references" / "06_troubleshooting.md",
        SKILLS_ROOT / "experts" / "atacseq-expert-skill" / "SKILL.md",
        SKILLS_ROOT
        / "experts"
        / "atacseq-expert-skill"
        / "references"
        / "01_scope_and_assumptions.md",
        SKILLS_ROOT / "experts" / "atacseq-expert-skill" / "references" / "06_troubleshooting.md",
        SKILLS_ROOT / "experts" / "fetchngs-expert-skill" / "SKILL.md",
        SKILLS_ROOT / "meta" / "pipeline-expert-skill-creator" / "SKILL.md",
        SKILLS_ROOT
        / "meta"
        / "pipeline-expert-skill-creator"
        / "references"
        / "03_rendering_rules.md",
        SKILLS_ROOT / "meta" / "pipeline-expert-skill-creator" / "assets" / "extraction-rules.yaml",
        SKILLS_ROOT
        / "meta"
        / "pipeline-expert-skill-creator"
        / "assets"
        / "validation-checklist.yaml",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    assert "`status`, `exit_code`, `job_dir`, `nextflow_log`" not in content
    assert "missing inputs, resume hints, and expected artifacts" not in content
    assert 'run_get(detail="full")' in content
    assert "path checks" in content
    assert "path warnings" in content
    assert "from_run_id" in content
    assert "restart compatibility" in content or "resume compatibility" in content
    assert "expected artifact" in content or "artifact_summary" in content
    assert "`run_layout`" in content
    assert "`layout_warnings`" in content
    assert "`project`" in content
    assert "`runs/<run_id>/work`" in content
    assert "`results/<run_id>`" in content


def test_expert_skill_assets_follow_run_layout_directory_contract() -> None:
    checked_files = [
        SKILLS_ROOT / "experts" / "ampliseq-expert-skill" / "assets" / "pipeline-profile.yaml",
        SKILLS_ROOT / "experts" / "ampliseq-expert-skill" / "assets" / "step-recipes.yaml",
        SKILLS_ROOT / "experts" / "ampliseq-expert-skill" / "assets" / "playbooks.yaml",
        SKILLS_ROOT / "experts" / "mag-expert-skill" / "assets" / "pipeline-profile.yaml",
        SKILLS_ROOT / "experts" / "mag-expert-skill" / "assets" / "step-recipes.yaml",
        SKILLS_ROOT / "experts" / "mag-expert-skill" / "assets" / "playbooks.yaml",
        SKILLS_ROOT / "experts" / "nanoseq-expert-skill" / "assets" / "pipeline-profile.yaml",
        SKILLS_ROOT / "experts" / "nanoseq-expert-skill" / "assets" / "step-recipes.yaml",
        SKILLS_ROOT / "experts" / "nanoseq-expert-skill" / "assets" / "playbooks.yaml",
        SKILLS_ROOT / "experts" / "rnaseq-expert-skill" / "assets" / "pipeline-profile.yaml",
        SKILLS_ROOT / "experts" / "rnaseq-expert-skill" / "assets" / "step-recipes.yaml",
        SKILLS_ROOT / "experts" / "atacseq-expert-skill" / "assets" / "pipeline-profile.yaml",
        SKILLS_ROOT / "experts" / "atacseq-expert-skill" / "assets" / "step-recipes.yaml",
        SKILLS_ROOT / "experts" / "fetchngs-expert-skill" / "assets" / "pipeline-profile.yaml",
        SKILLS_ROOT / "experts" / "fetchngs-expert-skill" / "assets" / "step-recipes.yaml",
        SKILLS_ROOT / "experts" / "fetchngs-expert-skill" / "assets" / "playbooks.yaml",
        SKILLS_ROOT / "experts" / "riboseq-expert-skill" / "assets" / "pipeline-profile.yaml",
        SKILLS_ROOT / "experts" / "riboseq-expert-skill" / "assets" / "step-recipes.yaml",
        SKILLS_ROOT / "experts" / "riboseq-expert-skill" / "assets" / "playbooks.yaml",
        SKILLS_ROOT / "experts" / "scrnaseq-expert-skill" / "assets" / "pipeline-profile.yaml",
        SKILLS_ROOT / "experts" / "scrnaseq-expert-skill" / "assets" / "step-recipes.yaml",
        SKILLS_ROOT / "experts" / "scrnaseq-expert-skill" / "assets" / "playbooks.yaml",
        SKILLS_ROOT / "experts" / "sarek-expert-skill" / "assets" / "pipeline-profile.yaml",
        SKILLS_ROOT / "experts" / "sarek-expert-skill" / "assets" / "step-recipes.yaml",
        SKILLS_ROOT / "experts" / "sarek-expert-skill" / "assets" / "playbooks.yaml",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    assert "run_layout" in content
    assert "layout_warnings" in content
    assert "runs/<run_id>/job" in content
    assert "runs/<run_id>/work" in content
    assert "results/<run_id>" in content
    assert "project-owned run root" in content


def test_pipeline_expert_skill_creator_separates_authoring_and_runtime_tool_surfaces() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-expert-skill-creator"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "extraction-rules.yaml",
        meta_skill_dir / "assets" / "validation-checklist.yaml",
        meta_skill_dir / "assets" / "templates" / "frontmatter.yaml",
        meta_skill_dir / "references" / "01_source_inventory.md",
        meta_skill_dir / "references" / "02_extraction_workflow.md",
        meta_skill_dir / "references" / "03_rendering_rules.md",
        meta_skill_dir / "references" / "04_validation.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)
    output_surface_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "extraction-rules.yaml",
        meta_skill_dir / "assets" / "templates" / "frontmatter.yaml",
        meta_skill_dir / "references" / "01_source_inventory.md",
        meta_skill_dir / "references" / "02_extraction_workflow.md",
    ]
    output_surface_content = "\n".join(
        path.read_text(encoding="utf-8") for path in output_surface_files
    )

    assert "skill-creator" in content
    assert "nextflow_inspect_pipeline" in content
    assert "project_list" in content
    assert "project_get" in content
    assert "nextflow_run" in content
    assert "run_list" in content
    assert "run_get" in content
    assert "run_artifacts" in content
    assert "run_logs" in content
    assert "`params`" in content
    assert "`config_files`" in content
    assert "`project`" in content
    assert "`run_id` / `run_name`" in content
    assert "`from_run_id`" in content
    assert "Do not tell the runtime agent to start ordinary planning or execution with" in content
    for removed_tool_name in REMOVED_TOOL_NAMES:
        assert removed_tool_name not in output_surface_content


def test_pipeline_expert_skill_creator_uses_from_run_id_as_only_public_restart_route() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-expert-skill-creator"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "extraction-rules.yaml",
        meta_skill_dir / "assets" / "validation-checklist.yaml",
        meta_skill_dir / "references" / "02_extraction_workflow.md",
        meta_skill_dir / "references" / "03_rendering_rules.md",
        meta_skill_dir / "references" / "04_validation.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    assert "`from_run_id` is the only public restart path" in content
    assert "`launch_spec`" in content
    assert "`nextflow_session_uuid`" in content
    assert "`resume_compatible`" in content
    assert "Do not teach `resume` or" in content
    assert "`resume_session_id` as public `nextflow_run` inputs." in content
    assert "`resume` / `resume_session_id` control restart behavior" not in content


def test_pipeline_expert_skill_creator_requires_server_path_boundary_language() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-expert-skill-creator"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "extraction-rules.yaml",
        meta_skill_dir / "assets" / "validation-checklist.yaml",
        meta_skill_dir / "assets" / "templates" / "frontmatter.yaml",
        meta_skill_dir / "references" / "01_source_inventory.md",
        meta_skill_dir / "references" / "02_extraction_workflow.md",
        meta_skill_dir / "references" / "03_rendering_rules.md",
        meta_skill_dir / "references" / "04_validation.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    assert "nextmcp server filesystem" in content
    assert "server-local" in content
    assert "client-local" in content
    assert "<server_input_root>" in content


def test_pipeline_expert_skill_creator_documents_parameter_selection_heuristic() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-expert-skill-creator"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "references" / "02_extraction_workflow.md",
        meta_skill_dir / "references" / "03_rendering_rules.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "progressive disclosure",
        "fixed allowlist",
        "historical reuse safety",
        "`params` versus `config_files`",
        "generic validation",
        "artifact contracts",
        "QC rules",
    ):
        assert token in content


def test_pipeline_expert_skill_creator_requires_progressive_schema_layout_contract() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-expert-skill-creator"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "asset-schema.yaml",
        meta_skill_dir / "assets" / "templates" / "expert-skill-layout.yaml",
        meta_skill_dir / "assets" / "extraction-rules.yaml",
        meta_skill_dir / "assets" / "validation-checklist.yaml",
        meta_skill_dir / "references" / "01_source_inventory.md",
        meta_skill_dir / "references" / "02_extraction_workflow.md",
        meta_skill_dir / "references" / "03_rendering_rules.md",
        meta_skill_dir / "references" / "04_validation.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "schema-index.yaml",
        "schema-groups",
        "04_schema_lookup.md",
        "06_troubleshooting.md",
        "full current-schema parameter coverage",
        "grouped parameter",
        "exact lookup",
    ):
        assert token in content


def test_pipeline_expert_skill_creator_defines_default_schema_groups_and_field_contract() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-expert-skill-creator"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "asset-schema.yaml",
        meta_skill_dir / "assets" / "extraction-rules.yaml",
        meta_skill_dir / "references" / "02_extraction_workflow.md",
        meta_skill_dir / "references" / "03_rendering_rules.md",
        meta_skill_dir / "references" / "04_validation.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "allOf",
        "definitions",
        "$defs",
        "input_output_options",
        "reference_genome_options",
        "alignment_options",
        "generic_options",
        "grouping_strategy",
        "selection_rule",
        "coverage_notes",
        "source_name",
        "classification",
        "channel",
        "example_values",
        "mapping_notes",
        "fallback",
        "route_shaping",
        "lookup_only",
        "non_runtime",
        "runtime_metadata",
        "authoring_only",
    ):
        assert token in content


def test_pipeline_expert_skill_creator_requires_capability_completeness() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-expert-skill-creator"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "extraction-rules.yaml",
        meta_skill_dir / "assets" / "validation-checklist.yaml",
        meta_skill_dir / "assets" / "templates" / "frontmatter.yaml",
        meta_skill_dir / "references" / "01_source_inventory.md",
        meta_skill_dir / "references" / "02_extraction_workflow.md",
        meta_skill_dir / "references" / "03_rendering_rules.md",
        meta_skill_dir / "references" / "04_validation.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    assert "significant optional capabilities" in content
    assert "explicitly scoped out" in content or "explicitly scope it out" in content
    for token in (
        "with_umi",
        "use_sentieon_star",
        "skip_pseudo_alignment",
        "kraken2_bracken",
        "STEP_BUILD_STAR_INDEX",
        "STEP_ASSEMBLE_STRINGTIE",
    ):
        assert token in content


def test_pipeline_expert_skill_creator_requires_resource_cap_config_rule() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-expert-skill-creator"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "extraction-rules.yaml",
        meta_skill_dir / "assets" / "validation-checklist.yaml",
        meta_skill_dir / "references" / "02_extraction_workflow.md",
        meta_skill_dir / "references" / "03_rendering_rules.md",
        meta_skill_dir / "references" / "04_validation.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "max_cpus",
        "max_memory",
        "max_time",
        "override config",
        "config_files",
        "process.resourceLimits",
        "params.max_cpus",
        "process.maxCpus",
    ):
        assert token in content


def test_pipeline_expert_skill_creator_encodes_historical_artifact_reuse_rules() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-expert-skill-creator"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "extraction-rules.yaml",
        meta_skill_dir / "assets" / "validation-checklist.yaml",
        meta_skill_dir / "references" / "01_source_inventory.md",
        meta_skill_dir / "references" / "02_extraction_workflow.md",
        meta_skill_dir / "references" / "03_rendering_rules.md",
        meta_skill_dir / "references" / "04_validation.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "run_list",
        "artifact_path_contains",
        "artifacts.json",
        "pipeline_fingerprint",
        "pipeline_info/params.json",
    ):
        assert token in content


def test_pipeline_expert_skill_creator_supports_repository_local_pipeline_sources() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-expert-skill-creator"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "extraction-rules.yaml",
        meta_skill_dir / "assets" / "validation-checklist.yaml",
        meta_skill_dir / "assets" / "templates" / "frontmatter.yaml",
        meta_skill_dir / "references" / "01_source_inventory.md",
        meta_skill_dir / "references" / "02_extraction_workflow.md",
        meta_skill_dir / "references" / "03_rendering_rules.md",
        meta_skill_dir / "references" / "04_validation.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "nf_pipeline/rnaseq",
        "nf_pipeline/riboseq",
        "inspect-equivalent",
        "repository-local",
        "nextflow_catalog.py",
        "build_authoring_bundle.py",
        "schema",
        "documents",
        "source_files",
        '"readme"',
        '"doc"',
        '"main_script"',
        '"nextflow_config"',
        '"entry_script"',
        '"workflow_script"',
    ):
        assert token in content


def test_pipeline_expert_skill_creator_keeps_repository_bundle_aligned_with_standard_inspect() -> (
    None
):
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-expert-skill-creator"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "extraction-rules.yaml",
        meta_skill_dir / "references" / "01_source_inventory.md",
        meta_skill_dir / "references" / "02_extraction_workflow.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "top-level `docs/*.md`",
        "top-level `*.nf` files other than `main.nf`",
        "top-level `workflows/*.nf`",
        "Nested workflow files such as `workflows/rnaseq/main.nf`",
        "not part of the standard bundle",
        "Do not silently pull in",
        "nested `docs/**` or `workflows/**` files",
    ):
        assert token in content


def test_riboseq_expert_skill_preserves_pipeline_specific_resource_override_shape() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "riboseq-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "references" / "03_parameters.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    _assert_resource_caps_use_config_files(content)
    assert "`runs/<run_id>/work`" not in content
    assert "Keep `work_dir` for work cache location" not in content


def test_nanoseq_expert_skill_covers_significant_optional_modes() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "nanoseq-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
        expert_skill_dir / "assets" / "playbooks.yaml",
        expert_skill_dir / "assets" / "step-recipes.yaml",
        expert_skill_dir / "assets" / "param-presets.yaml",
        expert_skill_dir / "assets" / "artifact-contracts.yaml",
        expert_skill_dir / "assets" / "qc-rules.yaml",
        expert_skill_dir / "references" / "01_scope_and_assumptions.md",
        expert_skill_dir / "references" / "02_playbooks.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "references" / "04_schema_lookup.md",
        expert_skill_dir / "references" / "05_outputs_and_qc.md",
        expert_skill_dir / "references" / "06_troubleshooting.md",
        expert_skill_dir / "evals" / "evals.json",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "skip_demultiplexing",
        "run_nanolyse",
        "skip_alignment",
        "call_variants",
        "variant_caller",
        "structural_variant_caller",
        "deepvariant_gpu",
        "quantification_method",
        "skip_modification_analysis",
        "skip_xpore",
        "skip_m6anet",
        "skip_fusion_analysis",
        "jaffal_ref_dir",
    ):
        assert token in content


def test_nanoseq_expert_skill_preserves_pipeline_specific_resource_override_shape() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "nanoseq-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    _assert_resource_caps_use_config_files(content)


def test_atacseq_expert_skill_preserves_pipeline_specific_resource_override_shape() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "atacseq-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "references" / "03_parameters.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    _assert_resource_caps_use_config_files(content)


def test_fetchngs_expert_skill_preserves_pipeline_specific_resource_override_shape() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "fetchngs-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
        expert_skill_dir / "assets" / "step-recipes.yaml",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    _assert_resource_caps_use_config_files(content)
    assert "<server_job_root>" not in content


def test_rnaseq_expert_skill_preserves_pipeline_specific_resource_override_shape() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "rnaseq-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    _assert_resource_caps_use_config_files(content)


def test_rnaseq_expert_skill_progressive_schema_assets_match_packaged_index() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "rnaseq-expert-skill"
    schema_index = yaml.safe_load(
        (expert_skill_dir / "assets" / "schema-index.yaml").read_text(encoding="utf-8")
    )
    assert schema_index["grouping_strategy"]

    actual_groups = {group["id"] for group in schema_index["groups"]}
    assert actual_groups

    collected_params: set[str] = set()
    for group in schema_index["groups"]:
        asset_path = expert_skill_dir / group["asset_path"]
        reference_path = expert_skill_dir / group["reference_path"]
        assert asset_path.is_file()
        assert reference_path.is_file()

        payload = yaml.safe_load(asset_path.read_text(encoding="utf-8"))
        assert payload["group"]["id"] == group["id"]
        assert payload["group"]["selection_rule"]
        assert payload["group"]["lookup_order"]
        assert payload["group"]["coverage_notes"]

        params = payload["parameters"]
        assert group["parameter_count"] == len(params)
        for param in params:
            collected_params.add(param["name"])
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

    assert len(collected_params) == sum(
        group["parameter_count"] for group in schema_index["groups"]
    )


def test_scrnaseq_expert_skill_preserves_pipeline_specific_resource_override_shape() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "scrnaseq-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    _assert_resource_caps_use_config_files(content)


def test_sarek_expert_skill_preserves_pipeline_specific_resource_override_shape() -> None:
    expert_skill_dir = SKILLS_ROOT / "experts" / "sarek-expert-skill"
    checked_files = [
        expert_skill_dir / "SKILL.md",
        expert_skill_dir / "references" / "03_parameters.md",
        expert_skill_dir / "assets" / "pipeline-profile.yaml",
        expert_skill_dir / "assets" / "step-recipes.yaml",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    _assert_resource_caps_use_config_files(content)
    assert (
        "process.withName" in content
        or "executor-specific overrides" in content
        or "resourceLimits" in content
    )
    assert "<server_job_root>" not in content


def test_pipeline_test_config_localizer_requires_recursive_download_and_rewrite_rules() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-test-config-localizer"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "workflow-rules.yaml",
        meta_skill_dir / "assets" / "output-contract.yaml",
        meta_skill_dir / "references" / "01_scope_and_boundaries.md",
        meta_skill_dir / "references" / "02_localization_workflow.md",
        meta_skill_dir / "references" / "03_prompt_rendering.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "samplesheet_local.csv",
        "rrna-db_local.txt",
        "nextmcp server filesystem",
        "server-local",
        "client-local",
        "raw.githubusercontent.com",
        "nextflow_run(prepare=true)",
        "official params",
        "process.resourceLimits",
    ):
        assert token in content


def test_pipeline_test_config_localizer_requires_resource_cap_override_rule() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-test-config-localizer"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "workflow-rules.yaml",
        meta_skill_dir / "assets" / "output-contract.yaml",
        meta_skill_dir / "references" / "01_scope_and_boundaries.md",
        meta_skill_dir / "references" / "02_localization_workflow.md",
        meta_skill_dir / "references" / "03_prompt_rendering.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "max_cpus",
        "max_memory",
        "max_time",
        "config_override_files",
        "nextflow_run(config_files=...)",
    ):
        assert token in content


def test_pipeline_test_config_localizer_requires_directory_mirroring_and_agent_mapping() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-test-config-localizer"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "workflow-rules.yaml",
        meta_skill_dir / "assets" / "output-contract.yaml",
        meta_skill_dir / "references" / "02_localization_workflow.md",
        meta_skill_dir / "references" / "03_prompt_rendering.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "Mirror the upstream directory structure",
        "downloads/<host>/<remote path>",
        "agent_param_mapping",
        "hide_raw_param_names_in_main_text",
        "samplesheet.csv -> `samplesheet_local.csv`",
    ):
        assert token in content


def test_pipeline_test_prompt_brief_rules_keep_client_brief_free_of_internal_mechanics() -> None:
    checked_files = [
        SKILLS_ROOT / "meta" / "pipeline-test-contract-builder" / "SKILL.md",
        SKILLS_ROOT / "meta" / "pipeline-test-converter" / "SKILL.md",
        SKILLS_ROOT
        / "meta"
        / "pipeline-test-converter"
        / "references"
        / "01-conversion-workflow.md",
        SKILLS_ROOT / "meta" / "pipeline-test-config-localizer" / "assets" / "output-contract.yaml",
        SKILLS_ROOT
        / "meta"
        / "pipeline-test-config-localizer"
        / "references"
        / "03_prompt_rendering.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "client-visible",
        "Available inputs",
        "Route constraints",
        "directly supported by the source materials",
        "conf/test.config",
        "tests/default.nf.test",
        "nextflow_run(prepare=true)",
        "config_files",
        "override config",
        "resource caps",
        "4 CPUs",
        "test, validation run, or production analysis",
    ):
        assert token in content


def test_pipeline_test_config_localizer_requires_progress_logging_for_helper_scripts() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-test-config-localizer"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "workflow-rules.yaml",
        meta_skill_dir / "references" / "02_localization_workflow.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "localize_testdata.py",
        "progress",
        "stderr",
        "final rewritten manifest path on stdout",
        "Localization complete",
    ):
        assert token in content


def test_pipeline_test_config_localizer_uses_project_mode_runtime_tools() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-test-config-localizer"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "workflow-rules.yaml",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    assert "project_get" in content
    assert "`project`" in content
    assert "run_layout" in content
    assert "process_get" not in content
    assert "process_logs" not in content
    assert "`cwd`" not in content


def test_pipeline_smoke_evaluator_uses_project_mode_evidence_fields() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-smoke-evaluator"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "references" / "01-evidence-bundle.md",
        meta_skill_dir / "references" / "02-client-evidence-collection-prompt.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "project",
        "run_name",
        "run_id",
        "project_id",
        "run_layout",
        "results_dir",
        "job_dir",
    ):
        assert token in content

    assert "`cwd`" not in content
    assert "`work_dir`" not in content


def test_pipeline_test_config_localizer_excludes_nf_test_harness_overrides_by_default() -> None:
    meta_skill_dir = SKILLS_ROOT / "meta" / "pipeline-test-config-localizer"
    checked_files = [
        meta_skill_dir / "SKILL.md",
        meta_skill_dir / "assets" / "workflow-rules.yaml",
        meta_skill_dir / "references" / "01_scope_and_boundaries.md",
        meta_skill_dir / "references" / "02_localization_workflow.md",
    ]
    content = "\n".join(path.read_text(encoding="utf-8") for path in checked_files)

    for token in (
        "tests/nextflow.config",
        "nf-test.config",
        "nf-test harness",
        "Do not automatically",
        "nextflow.config",
        "the user explicitly asks to reproduce nf-test behavior",
    ):
        assert token in content


def test_pipeline_test_localization_docs_require_missing_mirror_fallback() -> None:
    localizer_files = [
        SKILLS_ROOT / "meta" / "pipeline-test-config-localizer" / "SKILL.md",
        SKILLS_ROOT / "meta" / "pipeline-test-config-localizer" / "assets" / "output-contract.yaml",
        SKILLS_ROOT
        / "meta"
        / "pipeline-test-config-localizer"
        / "references"
        / "01_scope_and_boundaries.md",
        SKILLS_ROOT
        / "meta"
        / "pipeline-test-config-localizer"
        / "references"
        / "02_localization_workflow.md",
        SKILLS_ROOT
        / "meta"
        / "pipeline-test-config-localizer"
        / "references"
        / "03_prompt_rendering.md",
    ]
    localizer_content = "\n".join(path.read_text(encoding="utf-8") for path in localizer_files)

    for token in (
        "preferred optimization",
        "target files",
        "already exist",
        "missing expected local mirror",
        "self-contained bundle",
        "localized_root",
        "authoritative",
        "shared mirror root",
    ):
        assert token in localizer_content

    builder_converter_files = [
        SKILLS_ROOT / "meta" / "pipeline-test-contract-builder" / "SKILL.md",
        SKILLS_ROOT / "meta" / "pipeline-test-converter" / "SKILL.md",
    ]
    builder_converter_content = "\n".join(
        path.read_text(encoding="utf-8") for path in builder_converter_files
    )

    for token in (
        "Do not assume that a preferred shared mirror root already exists",
        "self-contained bundle under the current",
        "Do not default to external",
        "shared mirror roots unless the task explicitly depends on them",
    ):
        assert token in builder_converter_content


def _skill_source_dirs() -> list[Path]:
    return sorted(
        skill_dir
        for class_dir in SKILLS_ROOT.iterdir()
        if class_dir.is_dir() and class_dir.name in {"operator", "experts", "meta"}
        for skill_dir in class_dir.iterdir()
        if skill_dir.is_dir()
        if (skill_dir / "SKILL.md").is_file()
    )


def _expected_skill_class(skill_dir: Path) -> str:
    return {
        "operator": "operator",
        "experts": "expert",
        "meta": "meta",
    }[skill_dir.parent.name]


def _parse_skill_md(path: Path) -> tuple[dict[str, object], str]:
    content = path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(content)
    assert match is not None, f"Invalid frontmatter in {path}"

    frontmatter = yaml.safe_load(match.group(1))
    assert isinstance(frontmatter, dict)
    body = match.group(2)
    return frontmatter, body


def _assert_resource_caps_use_config_files(content: str) -> None:
    assert "config_files" in content
    assert "resource cap" in content or "Resource cap" in content
    assert (
        "process.resourceLimits" in content
        or "resourceLimits" in content
        or "process selector" in content
        or "process selectors" in content
        or "executor-specific overrides" in content
    )
