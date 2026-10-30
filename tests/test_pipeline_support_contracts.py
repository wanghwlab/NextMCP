"""Validation tests for pipeline support contract examples."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = REPO_ROOT / "tests" / "pipeline_support"
BASELINE_TASK_PIPELINES = tuple(
    sorted(
        path.parent.name
        for path in CONTRACT_ROOT.glob("*/smoke.task.md")
        if "baseline-noskill-" in path.read_text(encoding="utf-8")
    )
)

CLIENT_VISIBLE_BRIEF_HEADINGS = (
    "# Task",
    "## Available inputs",
)
CLIENT_VISIBLE_ROUTE_HEADINGS = ("## Route constraints", "## Workflow goal")

FORBIDDEN_BRIEF_SNIPPETS = (
    "## Localized inputs",
    "## Run requirements",
    "## Execution notes",
    "nextflow_run(prepare=true)",
    "nextflow_run(config_files",
    "config_files",
    "override config",
    "conf/test.config",
    "tests/default.nf.test",
    "tests/nextflow.config",
    "production analysis",
    "validation run",
    "function check",
    "server default profile",
    "work directory",
    "smoke test",
    "smoke run",
)

MAX_CPUS_PATTERN = re.compile(r"params\.max_cpus\s*=\s*(\d+)")
RESOURCE_LIMIT_CPUS_PATTERN = re.compile(r"cpus:\s*(\d+)")
MAX_MEMORY_PATTERN = re.compile(r"params\.max_memory\s*=\s*'([^']+)'")
RESOURCE_LIMIT_MEMORY_PATTERN = re.compile(r"memory:\s*'([^']+)'")
MAX_TIME_PATTERN = re.compile(r"params\.max_time\s*=\s*'([^']+)'")
RESOURCE_LIMIT_TIME_PATTERN = re.compile(r"time:\s*'([^']+)'")


def assert_brief_is_client_visible(brief: str) -> None:
    for heading in CLIENT_VISIBLE_BRIEF_HEADINGS:
        assert heading in brief
    assert any(heading in brief for heading in CLIENT_VISIBLE_ROUTE_HEADINGS)

    for snippet in FORBIDDEN_BRIEF_SNIPPETS:
        assert snippet not in brief


def prompt_brief_path(case_dir: Path, contract: dict[str, object]) -> Path:
    configured_path = contract.get("prompt_brief_path")
    if isinstance(configured_path, str):
        path = REPO_ROOT / configured_path
        assert path.is_file()
        return path

    return case_dir / "smoke.task.md"


def read_prompt_brief(case_dir: Path, contract: dict[str, object]) -> str:
    return prompt_brief_path(case_dir, contract).read_text(encoding="utf-8")


def assert_brief_uses_expected_project_names(brief: str, pipeline: str) -> None:
    if pipeline in BASELINE_TASK_PIPELINES:
        assert f"pipeline-withskill-{pipeline}" in brief
        assert f"baseline-noskill-{pipeline}" in brief
    else:
        assert f"pipeline-support-{pipeline}" in brief


def assert_brief_mentions_resource_caps(
    brief: str, *, cpus: int, memory: str, runtime: str
) -> None:
    expected = (
        f"Keep the upstream test resource caps at {cpus} CPUs, "
        f"{memory} memory, and {runtime} runtime."
    )
    assert expected in brief


def extract_resource_caps_from_contract(contract: dict[str, object]) -> tuple[int, str, str]:
    launch = contract["launch"]
    assert isinstance(launch, dict)

    config_overrides = launch.get("config_overrides")
    assert isinstance(config_overrides, list) and config_overrides

    for item in config_overrides:
        assert isinstance(item, dict)
        content = item.get("content")
        if not isinstance(content, str):
            continue

        cpus_match = MAX_CPUS_PATTERN.search(content) or RESOURCE_LIMIT_CPUS_PATTERN.search(content)
        memory_match = MAX_MEMORY_PATTERN.search(content) or RESOURCE_LIMIT_MEMORY_PATTERN.search(
            content
        )
        time_match = MAX_TIME_PATTERN.search(content) or RESOURCE_LIMIT_TIME_PATTERN.search(content)

        if cpus_match and memory_match and time_match:
            return int(cpus_match.group(1)), memory_match.group(1), time_match.group(1)

    raise AssertionError("Expected resource cap values in launch.config_overrides")


def test_pipeline_support_contract_examples_are_parseable() -> None:
    contract_paths = sorted(
        path
        for path in CONTRACT_ROOT.glob("*/*.yaml")
        if not path.name.endswith(".localization.yaml")
    )
    assert contract_paths

    for path in contract_paths:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict), path

        assert payload["version"] == 1
        assert payload["kind"] == "pipeline_support_contract"
        assert isinstance(payload["pipeline"], str) and payload["pipeline"]
        assert isinstance(payload["case_id"], str) and payload["case_id"]

        source_profile = payload["source_profile"]
        assert isinstance(source_profile, dict), path
        assert source_profile["config"].startswith("conf/test"), path

        local_data_contract = payload["local_data_contract"]
        assert isinstance(local_data_contract, dict), path
        assert isinstance(local_data_contract["localized_root"], str)

        launch = payload["launch"]
        assert isinstance(launch, dict), path
        assert launch["pipeline"] == payload["pipeline"]
        assert launch["project"] == f"pipeline-support-{payload['pipeline']}"
        assert launch["run_name"] == payload["case_id"]
        assert "cwd" not in launch
        assert "work_dir" not in launch
        assert isinstance(launch["params"], dict) and launch["params"]
        assert "outdir" not in launch["params"]
        if "config_files" in launch:
            assert isinstance(launch["config_files"], list) and launch["config_files"], path
            assert all(isinstance(item, str) and item for item in launch["config_files"]), path
        if "config_overrides" in launch:
            assert isinstance(launch["config_overrides"], list) and launch["config_overrides"], path
            for item in launch["config_overrides"]:
                assert isinstance(item, dict), path
                assert isinstance(item["path"], str) and item["path"], path
                assert isinstance(item["content"], str) and item["content"], path

        assertions = payload["assertions"]
        assert isinstance(assertions, dict), path
        assert assertions["prepare"]["ok"] is True
        assert assertions["run"]["ok"] is True


@pytest.mark.parametrize("pipeline", BASELINE_TASK_PIPELINES)
def test_baseline_task_prompts_preserve_contract_resource_caps(pipeline: str) -> None:
    prompt_path = CONTRACT_ROOT / pipeline / "smoke.task.md"
    contract_path = CONTRACT_ROOT / pipeline / "smoke.yaml"

    prompt = prompt_path.read_text(encoding="utf-8")
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))

    cpus, memory, runtime = extract_resource_caps_from_contract(contract)
    assert_brief_mentions_resource_caps(prompt, cpus=cpus, memory=memory, runtime=runtime)


def test_epitopeprediction_smoke_support_files_are_consistent() -> None:
    case_dir = CONTRACT_ROOT / "epitopeprediction"
    contract_path = case_dir / "smoke.yaml"
    localization_path = case_dir / "smoke.localization.yaml"
    script_path = case_dir / "localize_testdata.py"

    if not contract_path.exists():
        pytest.skip("epitopeprediction support case is not present in this checkout")

    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    localization = yaml.safe_load(localization_path.read_text(encoding="utf-8"))
    brief = read_prompt_brief(case_dir, contract)

    assert localization["kind"] == "pipeline_test_localization"
    assert localization["pipeline"] == contract["pipeline"]
    assert localization["case_id"] == contract["case_id"]
    assert localization["localized_root"] == contract["local_data_contract"]["localized_root"]

    rewritten_manifest = localization["rewritten_manifests"][0]
    expected_path = contract["local_data_contract"]["rewritten_manifests"][0]["expected_path"]
    assert rewritten_manifest["localized_path"] == expected_path
    assert contract["launch"]["inputs"]["input"] == expected_path
    roles = {entry["role"] for entry in localization["url_inventory"]}
    assert roles == {
        "input_samplesheet",
        "human_alleles_file",
        "mouse_alleles_file",
        "peptides_tsv",
    }

    mapped_params = {
        entry["official_param"]
        for entry in localization["agent_param_mapping"]
        if entry["official_param"] is not None
    }
    assert {
        "input",
        "tools",
        "min_peptide_length_classI",
        "max_peptide_length_classI",
    }.issubset(mapped_params)

    assert_brief_is_client_visible(brief)
    assert script_path.is_file()


def test_sarek_smoke_support_files_are_consistent() -> None:
    case_dir = CONTRACT_ROOT / "sarek"
    contract_path = case_dir / "smoke.yaml"
    localization_path = case_dir / "smoke.localization.yaml"
    script_path = case_dir / "localize_testdata.py"

    if not contract_path.exists():
        pytest.skip("sarek support case is not present in this checkout")

    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    localization = yaml.safe_load(localization_path.read_text(encoding="utf-8"))
    brief = read_prompt_brief(case_dir, contract)

    assert localization["kind"] == "pipeline_test_localization"
    assert localization["pipeline"] == contract["pipeline"]
    assert localization["case_id"] == contract["case_id"]
    assert localization["localized_root"] == contract["local_data_contract"]["localized_root"]

    rewritten_manifest = localization["rewritten_manifests"][0]
    expected_path = contract["local_data_contract"]["rewritten_manifests"][0]["expected_path"]
    assert rewritten_manifest["localized_path"] == expected_path
    assert contract["launch"]["inputs"]["input"] == expected_path

    copied_roles = {entry["role"] for entry in localization["local_file_inventory"]}
    assert copied_roles == {
        "input_samplesheet_template",
        "bcftools_header_template",
    }

    url_roles = {entry["role"] for entry in localization["url_inventory"]}
    assert {
        "fastq_read_1",
        "fastq_read_2",
        "bcftools_annotations",
        "bcftools_annotations_tbi",
        "dbsnp",
        "dbsnp_tbi",
        "genome_dict",
        "genome_fasta",
        "genome_fasta_fai",
        "germline_resource",
        "germline_resource_tbi",
        "intervals",
        "known_indels",
        "known_indels_tbi",
        "ngscheckmate_bed",
    } == url_roles

    mapped_params = {
        entry["official_param"]
        for entry in localization["agent_param_mapping"]
        if entry["official_param"] is not None
    }
    assert {
        "input",
        "bcftools_annotations",
        "bcftools_annotations_tbi",
        "bcftools_header_lines",
        "dbsnp",
        "dbsnp_tbi",
        "dict",
        "fasta",
        "fasta_fai",
        "germline_resource",
        "germline_resource_tbi",
        "intervals",
        "known_indels",
        "known_indels_tbi",
        "ngscheckmate_bed",
        "snpeff_db",
        "vep_cache_version",
        "vep_genome",
        "vep_species",
        "dbsnp_vqsr",
        "known_indels_vqsr",
        "split_fastq",
        "tools",
    }.issubset(mapped_params)

    ignored_fields = {entry["config_field"] for entry in localization["ignored_upstream_params"]}
    assert ignored_fields == {"genome", "sentieon_dnascope_model"}

    assert_brief_is_client_visible(brief)
    assert "igenomes_ignore" in brief
    assert script_path.is_file()


def test_scrnaseq_smoke_support_files_are_consistent() -> None:
    case_dir = CONTRACT_ROOT / "scrnaseq"
    contract_path = case_dir / "smoke.yaml"
    localization_path = case_dir / "smoke.localization.yaml"
    script_path = case_dir / "localize_testdata.py"

    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    localization = yaml.safe_load(localization_path.read_text(encoding="utf-8"))
    brief = read_prompt_brief(case_dir, contract)

    assert localization["kind"] == "pipeline_test_localization"
    assert localization["pipeline"] == contract["pipeline"]
    assert localization["case_id"] == contract["case_id"]
    assert localization["localized_root"] == contract["local_data_contract"]["localized_root"]

    rewritten_manifest = localization["rewritten_manifests"][0]
    expected_path = contract["local_data_contract"]["rewritten_manifests"][0]["expected_path"]
    assert rewritten_manifest["localized_path"] == expected_path
    assert contract["launch"]["params"]["input"] == expected_path

    url_roles = {entry["role"] for entry in localization["url_inventory"]}
    assert url_roles == {
        "input_samplesheet",
        "genome_fasta",
        "annotation_gtf",
        "sample_x_read_1",
        "sample_x_read_2",
        "sample_y_lane_1_read_1",
        "sample_y_lane_1_read_2",
        "sample_y_lane_2_read_1",
        "sample_y_lane_2_read_2",
    }

    mapped_params = {
        entry["official_param"]
        for entry in localization["agent_param_mapping"]
        if entry["official_param"] is not None
    }
    assert {
        "input",
        "fasta",
        "gtf",
        "aligner",
        "protocol",
        "skip_cellbender",
        "validationSchemaIgnoreParams",
    }.issubset(mapped_params)
    assert contract["launch"]["config_files"] == [
        "/data/nextmcp/testdata/scrnaseq/test/project-files/pipeline-support-scrnaseq/max_resources.config"
    ]
    assert contract["launch"]["config_files"] == [
        item["path"] for item in contract["launch"]["config_overrides"]
    ]
    assert localization["config_override_files"][0]["path"] == contract["launch"]["config_files"][0]
    assert "params.max_cpus = 2" in localization["config_override_files"][0]["content"]
    assert "params.max_memory = '6.GB'" in localization["config_override_files"][0]["content"]
    assert "params.max_time = '6.h'" in localization["config_override_files"][0]["content"]

    assert_brief_is_client_visible(brief)
    assert_brief_uses_expected_project_names(brief, "scrnaseq")
    assert "/data/analysis/pipeline-support" not in brief
    assert_brief_mentions_resource_caps(brief, cpus=2, memory="6.GB", runtime="6.h")
    assert script_path.is_file()


def test_atacseq_smoke_support_files_are_consistent() -> None:
    case_dir = CONTRACT_ROOT / "atacseq"
    contract_path = case_dir / "smoke.yaml"
    localization_path = case_dir / "smoke.localization.yaml"
    script_path = case_dir / "localize_testdata.py"

    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    localization = yaml.safe_load(localization_path.read_text(encoding="utf-8"))
    brief = read_prompt_brief(case_dir, contract)

    assert localization["kind"] == "pipeline_test_localization"
    assert localization["pipeline"] == contract["pipeline"]
    assert localization["case_id"] == contract["case_id"]
    assert localization["localized_root"] == contract["local_data_contract"]["localized_root"]

    rewritten_manifest = localization["rewritten_manifests"][0]
    expected_path = contract["local_data_contract"]["rewritten_manifests"][0]["expected_path"]
    assert rewritten_manifest["localized_path"] == expected_path
    assert contract["launch"]["params"]["input"] == expected_path

    url_roles = {entry["role"] for entry in localization["url_inventory"]}
    assert url_roles == {
        "input_samplesheet",
        "genome_fasta",
        "annotation_gtf",
    }

    mapped_params = {
        entry["official_param"]
        for entry in localization["agent_param_mapping"]
        if entry["official_param"] is not None
    }
    assert {
        "input",
        "aligner",
        "read_length",
        "mito_name",
        "fasta",
        "gtf",
        "fingerprint_bins",
        "validationSchemaIgnoreParams",
    }.issubset(mapped_params)
    assert contract["launch"]["config_files"] == [
        "/data/nextmcp/testdata/atacseq/test/project-files/pipeline-support-atacseq/max_resources.config"
    ]
    assert contract["launch"]["config_files"] == [
        item["path"] for item in contract["launch"]["config_overrides"]
    ]
    assert localization["config_override_files"][0]["path"] == contract["launch"]["config_files"][0]
    assert "params.max_cpus = 2" in localization["config_override_files"][0]["content"]
    assert "params.max_memory = '6.GB'" in localization["config_override_files"][0]["content"]
    assert "params.max_time = '6.h'" in localization["config_override_files"][0]["content"]

    assert_brief_is_client_visible(brief)
    assert_brief_uses_expected_project_names(brief, "atacseq")
    assert "/data/analysis/pipeline-support" not in brief
    assert_brief_mentions_resource_caps(brief, cpus=2, memory="6.GB", runtime="6.h")
    assert script_path.is_file()


def test_chipseq_smoke_support_files_are_consistent() -> None:
    case_dir = CONTRACT_ROOT / "chipseq"
    contract_path = case_dir / "smoke.yaml"
    localization_path = case_dir / "smoke.localization.yaml"
    script_path = case_dir / "localize_testdata.py"

    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    localization = yaml.safe_load(localization_path.read_text(encoding="utf-8"))
    brief = read_prompt_brief(case_dir, contract)

    assert localization["kind"] == "pipeline_test_localization"
    assert localization["pipeline"] == contract["pipeline"]
    assert localization["case_id"] == contract["case_id"]
    assert localization["localized_root"] == contract["local_data_contract"]["localized_root"]

    rewritten_manifest = localization["rewritten_manifests"][0]
    expected_path = contract["local_data_contract"]["rewritten_manifests"][0]["expected_path"]
    assert rewritten_manifest["localized_path"] == expected_path
    assert contract["launch"]["params"]["input"] == expected_path

    url_roles = {entry["role"] for entry in localization["url_inventory"]}
    assert url_roles == {
        "annotation_gtf",
        "genome_fasta",
        "input_samplesheet",
    }

    mapped_params = {
        entry["official_param"]
        for entry in localization["agent_param_mapping"]
        if entry["official_param"] is not None
    }
    assert {
        "aligner",
        "fasta",
        "fingerprint_bins",
        "gtf",
        "input",
        "read_length",
        "skip_preseq",
        "validationSchemaIgnoreParams",
    }.issubset(mapped_params)
    assert contract["launch"]["config_files"] == [
        "/data/nextmcp/testdata/chipseq/test/project-files/pipeline-support-chipseq/max_resources.config"
    ]
    assert contract["launch"]["config_files"] == [
        item["path"] for item in contract["launch"]["config_overrides"]
    ]
    assert localization["config_override_files"][0]["path"] == contract["launch"]["config_files"][0]
    assert "params.max_cpus = 2" in localization["config_override_files"][0]["content"]
    assert "params.max_memory = '6.GB'" in localization["config_override_files"][0]["content"]
    assert "params.max_time = '6.h'" in localization["config_override_files"][0]["content"]

    assert_brief_is_client_visible(brief)
    assert_brief_uses_expected_project_names(brief, "chipseq")
    assert_brief_mentions_resource_caps(brief, cpus=2, memory="6.GB", runtime="6.h")
    assert script_path.is_file()


def test_nanoseq_smoke_support_files_are_consistent() -> None:
    case_dir = CONTRACT_ROOT / "nanoseq"
    contract_path = case_dir / "smoke.yaml"
    localization_path = case_dir / "smoke.localization.yaml"
    script_path = case_dir / "localize_testdata.py"

    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    localization = yaml.safe_load(localization_path.read_text(encoding="utf-8"))
    brief = read_prompt_brief(case_dir, contract)

    assert contract["mode"] == "profile-only"
    assert contract["classification"]["primary_mode"] == "profile-only"
    assert contract["classification"]["modifiers"] == ["localize-remote-inputs"]

    assert localization["kind"] == "pipeline_test_localization"
    assert localization["pipeline"] == contract["pipeline"]
    assert localization["case_id"] == contract["case_id"]
    assert localization["localized_root"] == contract["local_data_contract"]["localized_root"]

    rewritten_manifest = localization["rewritten_manifests"][0]
    expected_path = contract["local_data_contract"]["rewritten_manifests"][0]["expected_path"]
    assert rewritten_manifest["localized_path"] == expected_path
    assert contract["launch"]["params"]["input"] == expected_path

    url_roles = {entry["role"] for entry in localization["url_inventory"]}
    assert url_roles == {
        "input_fastq",
        "input_samplesheet",
        "reference_fasta",
    }

    mapped_params = {
        entry["official_param"]
        for entry in localization["agent_param_mapping"]
        if entry["official_param"] is not None
    }
    assert {
        "aligner",
        "barcode_kit",
        "input",
        "input_path",
        "protocol",
        "skip_bigbed",
        "skip_bigwig",
        "skip_fusion_analysis",
        "skip_modification_analysis",
        "skip_quantification",
    }.issubset(mapped_params)

    ignored_fields = {entry["config_field"] for entry in localization["ignored_upstream_params"]}
    assert ignored_fields == {"params.outdir"}

    assert contract["launch"]["params"]["input_path"] == (
        "/data/nextmcp/testdata/nanoseq/test/pipeline-data/nanoseq/fastq/"
        "nondemultiplexed/sample_nobc_dx.fastq.gz"
    )
    assert contract["launch"]["config_files"] == [
        "/data/nextmcp/testdata/nanoseq/test/project-files/pipeline-support-nanoseq/max_resources.config"
    ]
    assert contract["launch"]["config_files"] == [
        item["path"] for item in contract["launch"]["config_overrides"]
    ]
    assert localization["config_override_files"][0]["path"] == contract["launch"]["config_files"][0]
    assert "params.max_cpus = 2" in localization["config_override_files"][0]["content"]
    assert "params.max_memory = '6.GB'" in localization["config_override_files"][0]["content"]
    assert "params.max_time = '12.h'" in localization["config_override_files"][0]["content"]

    required_paths = set(contract["assertions"]["artifacts"]["required_paths"])
    assert required_paths == {
        "qcat/fastq/barcode06.fastq.gz",
        "qcat/fastq/barcode12.fastq.gz",
        "fastqc",
        "nanoplot",
        "minimap2/sample_R1.sorted.bam",
        "minimap2/sample_R2.sorted.bam",
        "minimap2/samtools_stats",
        "multiqc/minimap2/multiqc_report.html",
        "pipeline_info/software_versions.yml",
    }

    localized_rows = rewritten_manifest["localized_rows"]
    assert localized_rows[0]["fasta"] == (
        "/data/nextmcp/testdata/nanoseq/test/pipeline-data/nanoseq/reference/hg19_KCMF1.fa"
    )
    assert localized_rows[1]["fasta"] == localized_rows[0]["fasta"]

    assert_brief_is_client_visible(brief)
    assert_brief_uses_expected_project_names(brief, "nanoseq")
    assert "/data/analysis/pipeline-support" not in brief
    assert "sample_nobc_dx.fastq.gz" in brief
    assert "hg19_KCMF1.fa" in brief
    assert "minimap2" in brief
    assert_brief_mentions_resource_caps(brief, cpus=2, memory="6.GB", runtime="12.h")
    assert contract["prompt_brief"].split() == brief.split()
    assert localization["natural_language_execution_brief"].split() == brief.split()
    assert script_path.is_file()


def test_mag_smoke_support_files_are_consistent() -> None:
    case_dir = CONTRACT_ROOT / "mag"
    contract_path = case_dir / "smoke.yaml"
    localization_path = case_dir / "smoke.localization.yaml"
    script_path = case_dir / "localize_testdata.py"

    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    localization = yaml.safe_load(localization_path.read_text(encoding="utf-8"))
    brief = read_prompt_brief(case_dir, contract)

    assert contract["mode"] == "profile-only"
    assert contract["classification"]["primary_mode"] == "profile-only"
    assert set(contract["classification"]["modifiers"]) == {
        "localize-remote-inputs",
        "snapshot-rich",
    }

    assert localization["kind"] == "pipeline_test_localization"
    assert localization["pipeline"] == contract["pipeline"]
    assert localization["case_id"] == contract["case_id"]
    assert localization["localized_root"] == contract["local_data_contract"]["localized_root"]

    rewritten_manifest = localization["rewritten_manifests"][0]
    expected_path = contract["local_data_contract"]["rewritten_manifests"][0]["expected_path"]
    assert rewritten_manifest["localized_path"] == expected_path
    assert contract["launch"]["params"]["input"] == expected_path

    url_roles = {entry["role"] for entry in localization["url_inventory"]}
    assert url_roles == {
        "input_samplesheet",
        "busco_database",
        "gtdbtk_database",
        "cat_database",
        "test_minigut_read_1",
        "test_minigut_read_2",
        "test_minigut_sample2_read_1",
        "test_minigut_sample2_read_2",
    }

    mapped_params = {
        entry["official_param"]
        for entry in localization["agent_param_mapping"]
        if entry["official_param"] is not None
    }
    assert {
        "input",
        "min_length_unbinned_contigs",
        "max_unbinned_contigs",
        "skip_ale",
        "skip_concoct",
        "skip_comebin",
        "skip_metabinner",
        "busco_db",
        "busco_db_lineage",
        "busco_clean",
        "prokka_fast_mode",
        "gtdb_db",
        "cat_db",
        "cat_no_suggestive_asterisks",
        "gtdbtk_min_completeness",
        "gtdbtk_skip_aniscreen",
        "gtdbtk_use_full_tree",
        "megahit_fix_cpu_1",
        "spades_fix_cpus",
    }.issubset(mapped_params)

    ignored_fields = {entry["config_field"] for entry in localization["ignored_upstream_params"]}
    assert ignored_fields == {
        "tests/nextflow.config:params.pipelines_testdata_base_path",
        "tests/nextflow.config:params.modules_testdata_base_path",
        "tests/nextflow.config:aws.client.anonymous",
        "process.withName:'PROKKA'",
        "params.outdir",
    }

    assert contract["launch"]["config_files"] == [
        "/data/nextmcp/testdata/mag/test/project-files/pipeline-support-mag/profile_test_overrides.config"
    ]
    assert contract["launch"]["config_files"] == [
        item["path"] for item in contract["launch"]["config_overrides"]
    ]
    assert localization["config_override_files"][0]["path"] == contract["launch"]["config_files"][0]
    override_content = localization["config_override_files"][0]["content"]
    assert "cpus: 4" in override_content
    assert "memory: '15.GB'" in override_content
    assert "time: '1.h'" in override_content

    required_paths = set(contract["assertions"]["artifacts"]["required_paths"])
    assert required_paths == {
        "multiqc/multiqc_report.html",
        "multiqc/multiqc_data/busco_plot_bacteria_odb10.yaml",
        "multiqc/multiqc_data/multiqc_general_stats.yaml",
        "multiqc/multiqc_data/multiqc_gtdbtk.yaml",
        "multiqc/multiqc_data/multiqc_prokka.yaml",
        "multiqc/multiqc_data/multiqc_quast.yaml",
        "pipeline_info/nf_core_mag_software_mqc_versions.yml",
    }

    assert_brief_is_client_visible(brief)
    assert_brief_uses_expected_project_names(brief, "mag")
    assert "/data/analysis/pipeline-support" not in brief
    assert "tests/nextflow.config" not in brief
    assert_brief_mentions_resource_caps(brief, cpus=4, memory="15.GB", runtime="1.h")
    assert script_path.is_file()


def test_methylseq_smoke_support_files_are_consistent() -> None:
    case_dir = CONTRACT_ROOT / "methylseq"
    contract_path = case_dir / "smoke.yaml"
    localization_path = case_dir / "smoke.localization.yaml"
    script_path = case_dir / "localize_testdata.py"

    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    localization = yaml.safe_load(localization_path.read_text(encoding="utf-8"))
    brief = read_prompt_brief(case_dir, contract)

    assert contract["mode"] == "profile-only"
    assert contract["classification"]["primary_mode"] == "profile-only"
    assert set(contract["classification"]["modifiers"]) == {
        "localize-remote-inputs",
        "snapshot-rich",
    }

    assert localization["kind"] == "pipeline_test_localization"
    assert localization["pipeline"] == contract["pipeline"]
    assert localization["case_id"] == contract["case_id"]
    assert localization["localized_root"] == contract["local_data_contract"]["localized_root"]

    rewritten_manifest = localization["rewritten_manifests"][0]
    expected_path = contract["local_data_contract"]["rewritten_manifests"][0]["expected_path"]
    assert rewritten_manifest["localized_path"] == expected_path
    assert contract["launch"]["inputs"]["input"] == expected_path

    assert contract["launch"]["config_files"] == [
        "/data/nextmcp/testdata/methylseq/test/project-files/pipeline-support-methylseq/profile_test_overrides.config"
    ]
    assert contract["launch"]["config_files"] == [
        item["path"] for item in contract["launch"]["config_overrides"]
    ]
    assert localization["config_override_files"][0]["path"] == contract["launch"]["config_files"][0]
    override_content = localization["config_override_files"][0]["content"]
    assert "cpus: 4" in override_content
    assert "memory: '15.GB'" in override_content
    assert "time: '1.h'" in override_content

    required_paths = set(contract["assertions"]["artifacts"]["required_paths"])
    assert required_paths == {
        "bismark/deduplicated/Ecoli_10K_methylated.deduplicated.sorted.bam",
        "bismark/deduplicated/SRR389222_sub1.deduplicated.sorted.bam",
        "bismark/methylation_calls/methylation_coverage/SRR389222_sub1_trimmed_bismark_bt2.deduplicated.bismark.cov.gz",
        "bismark/summary/bismark_summary_report.html",
        "multiqc/bismark/multiqc_report.html",
        "multiqc/bismark/multiqc_data/multiqc_bismark_alignment.txt",
        "pipeline_info/nf_core_methylseq_software_mqc_versions.yml",
        "pipeline_info/nf_core_methylseq_topic_versions.yml",
    }

    content_checks = {
        entry["path"]: (entry["kind"], entry["expected"])
        for entry in contract["assertions"]["artifacts"]["content_checks"]
    }
    coverage_path = (
        "bismark/methylation_calls/methylation_coverage/"
        "SRR389222_sub1_trimmed_bismark_bt2.deduplicated.bismark.cov.gz"
    )
    assert content_checks == {
        coverage_path: (
            "gunzip_md5",
            "5377d9fff4f1bf5b98dc2310fbeb6ec9",
        ),
        "multiqc/bismark/multiqc_data/multiqc_bismark_alignment.txt": (
            "md5",
            "8ee2e88d6b5c1411b4665b02f82ae1b7",
        ),
        "multiqc/bismark/multiqc_data/multiqc_cutadapt.txt": (
            "md5",
            "883891ac4901385102be053212068732",
        ),
    }

    assert_brief_is_client_visible(brief)
    assert_brief_uses_expected_project_names(brief, "methylseq")
    assert "/data/analysis/pipeline-support" not in brief
    assert "Bismark" in brief
    assert_brief_mentions_resource_caps(brief, cpus=4, memory="15.GB", runtime="1.h")
    assert contract["prompt_brief"].split() == brief.split()
    assert localization["natural_language_execution_brief"].split() == brief.split()
    assert script_path.is_file()


def test_ampliseq_smoke_support_files_are_consistent() -> None:
    case_dir = CONTRACT_ROOT / "ampliseq"
    contract_path = case_dir / "smoke.yaml"
    localization_path = case_dir / "smoke.localization.yaml"
    script_path = case_dir / "localize_testdata.py"

    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    localization = yaml.safe_load(localization_path.read_text(encoding="utf-8"))
    brief = read_prompt_brief(case_dir, contract)

    assert contract["mode"] == "profile-only"
    assert contract["classification"]["primary_mode"] == "profile-only"
    assert set(contract["classification"]["modifiers"]) == {
        "localize-remote-inputs",
        "snapshot-rich",
    }

    assert localization["kind"] == "pipeline_test_localization"
    assert localization["pipeline"] == contract["pipeline"]
    assert localization["case_id"] == contract["case_id"]
    assert localization["localized_root"] == contract["local_data_contract"]["localized_root"]

    rewritten_manifest = localization["rewritten_manifests"][0]
    expected_path = contract["local_data_contract"]["rewritten_manifests"][0]["expected_path"]
    assert rewritten_manifest["localized_path"] == expected_path
    assert contract["launch"]["params"]["input"] == expected_path
    assert contract["launch"]["params"]["qiime_ref_tax_custom"] == (
        "/data/nextmcp/testdata/ampliseq/test/rewrites/downloads/data.qiime2.org/2023.7/"
        "tutorials/training-feature-classifiers/greengenes85.fna,"
        "/data/nextmcp/testdata/ampliseq/test/rewrites/downloads/data.qiime2.org/2023.7/"
        "tutorials/training-feature-classifiers/greengenes85.tax"
    )

    url_inventory = {entry["role"]: entry for entry in localization["url_inventory"]}
    url_roles = set(url_inventory)
    assert url_roles == {
        "input_samplesheet",
        "metadata_table",
        "qiime_greengenes85_fasta",
        "qiime_greengenes85_taxonomy",
        "sampleID_1a_read_1",
        "sampleID_1a_read_2",
        "sampleID_1_read_1",
        "sampleID_1_read_2",
        "sampleID_2a_read_1",
        "sampleID_2a_read_2",
        "sampleID_2_read_1",
        "sampleID_2_read_2",
    }
    assert url_inventory["qiime_greengenes85_taxonomy"]["download_redirect_target"] == (
        "https://s3-us-west-2.amazonaws.com/qiime2-data/2023.7/tutorials/"
        "training-feature-classifiers/85_otu_taxonomy.txt"
    )

    mapped_params = {
        entry["official_param"]
        for entry in localization["agent_param_mapping"]
        if entry["official_param"] is not None
    }
    assert {
        "input",
        "metadata",
        "FW_primer",
        "RV_primer",
        "dada_ref_taxonomy",
        "cut_dada_ref_taxonomy",
        "qiime_ref_tax_custom",
        "max_len_asv",
        "filter_ssu",
        "min_samples",
        "min_frequency",
        "metadata_category_barplot",
        "tax_agglom_max",
        "sbdiexport",
        "qiime_adonis_formula",
        "diversity_rarefaction_depth",
        "vsearch_cluster",
        "ancombc",
        "ancombc_formula",
        "ancombc_formula_reflvl",
        "ancombc_effect_size",
        "ancombc_significance",
    }.issubset(mapped_params)

    ignored_fields = {entry["config_field"] for entry in localization["ignored_upstream_params"]}
    assert ignored_fields == {
        "tests/nextflow.config:params.pipelines_testdata_base_path",
        "tests/nextflow.config:params.modules_testdata_base_path",
        "tests/nextflow.config:aws.client.anonymous",
        "params.outdir",
    }

    assert contract["launch"]["config_files"] == [
        "/data/nextmcp/testdata/ampliseq/test/project-files/pipeline-support-ampliseq/profile_test_overrides.config"
    ]
    assert contract["launch"]["config_files"] == [
        item["path"] for item in contract["launch"]["config_overrides"]
    ]
    assert localization["config_override_files"][0]["path"] == contract["launch"]["config_files"][0]
    override_content = localization["config_override_files"][0]["content"]
    assert "cpus: 4" in override_content
    assert "memory: '15.GB'" in override_content
    assert "time: '1.h'" in override_content
    assert "FW_primer" not in override_content
    assert "RV_primer" not in override_content
    assert "ancombc_significance" not in override_content
    assert any("SBDIEXPORT" in note and "null" in note for note in contract["launch"]["notes"])
    assert "ext.args" in localization["runtime_hints"]["launch_rule"]
    assert "null" in localization["runtime_hints"]["launch_rule"]

    prepare_required_paths = set(contract["assertions"]["prepare"]["required_paths"])
    assert {
        "/data/nextmcp/testdata/ampliseq/test/downloads/data.qiime2.org/2023.7/tutorials/training-feature-classifiers/85_otus.fasta",
        "/data/nextmcp/testdata/ampliseq/test/downloads/data.qiime2.org/2023.7/tutorials/training-feature-classifiers/85_otu_taxonomy.txt",
        "/data/nextmcp/testdata/ampliseq/test/rewrites/downloads/data.qiime2.org/2023.7/tutorials/training-feature-classifiers/greengenes85.fna",
        "/data/nextmcp/testdata/ampliseq/test/rewrites/downloads/data.qiime2.org/2023.7/tutorials/training-feature-classifiers/greengenes85.tax",
    }.issubset(prepare_required_paths)

    required_paths = set(contract["assertions"]["artifacts"]["required_paths"])
    assert required_paths == {
        "summary_report/summary_report.html",
        "overall_summary.tsv",
        "dada2/DADA2_stats.tsv",
        "dada2/ASV_table.tsv",
        "multiqc/multiqc_report.html",
        "multiqc/multiqc_data/multiqc_fastqc.txt",
        "multiqc/multiqc_data/multiqc_general_stats.txt",
        "multiqc/multiqc_data/multiqc_cutadapt.txt",
        "SBDI/dna.tsv",
        "vsearch_cluster/ASV_post_clustering_filtered.table.tsv",
    }

    content_checks = {
        entry["path"]: entry["expected"]
        for entry in contract["assertions"]["artifacts"]["content_checks"]
    }
    assert content_checks == {
        "overall_summary.tsv": "a20dea9e5f4ca80723d31494399510fc",
        "dada2/DADA2_stats.tsv": "54a1ac8d6c5a3ff15f700c4b2dd40c86",
        "dada2/ASV_table.tsv": "2618251e597593e4d716dd9bed095539",
        "multiqc/multiqc_data/multiqc_fastqc.txt": "7d23984b06e4251f17e1cfce7a04aaae",
        "multiqc/multiqc_data/multiqc_general_stats.txt": "885c19ff3e53d16bfe7937d6694268d7",
        "multiqc/multiqc_data/multiqc_cutadapt.txt": "3dce058d2d6c85a3cca7314ae19c5586",
        "SBDI/dna.tsv": "46bb52a05204ade2d571ac089f732012",
        "vsearch_cluster/ASV_post_clustering_filtered.table.tsv": (
            "e607469a32d490bbe139e9196ff4a47d"
        ),
    }

    assert_brief_is_client_visible(brief)
    assert_brief_uses_expected_project_names(brief, "ampliseq")
    assert "/data/analysis/pipeline-support" not in brief
    assert (
        "/data/nextmcp/testdata/ampliseq/test/pipeline-data/ampliseq/samplesheets/Metadata.tsv"
        in brief
    )
    assert (
        "/data/nextmcp/testdata/ampliseq/test/rewrites/downloads/data.qiime2.org/2023.7/tutorials/"
        "training-feature-classifiers/greengenes85.tax" in brief
    )
    assert "tests/nextflow.config" not in brief
    assert "DADA2" in brief
    assert "ANCOMBC" in brief
    assert "VSEARCH" in brief
    assert_brief_mentions_resource_caps(brief, cpus=4, memory="15.GB", runtime="1.h")
    assert contract["prompt_brief"].split() == brief.split()
    assert localization["natural_language_execution_brief"].split() == brief.split()
    assert script_path.is_file()


def test_rnaseq_smoke_support_files_are_consistent() -> None:
    case_dir = CONTRACT_ROOT / "rnaseq"
    contract_path = case_dir / "smoke.yaml"
    localization_path = case_dir / "smoke.localization.yaml"
    script_path = case_dir / "localize_testdata.py"

    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    localization = yaml.safe_load(localization_path.read_text(encoding="utf-8"))
    brief = read_prompt_brief(case_dir, contract)

    assert localization["kind"] == "pipeline_test_localization"
    assert localization["pipeline"] == contract["pipeline"]
    assert localization["case_id"] == contract["case_id"]
    assert localization["localized_root"] == contract["local_data_contract"]["localized_root"]
    assert localization["url_inventory"] == []
    assert localization["rewritten_manifests"] == []

    local_roles = {entry["role"] for entry in localization["local_file_inventory"]}
    assert local_roles == {
        "additional_fasta",
        "annotation_gff",
        "annotation_gtf",
        "bbsplit_fasta_list",
        "genome_fasta",
        "hisat2_index",
        "input_samplesheet",
        "salmon_index",
        "transcript_fasta",
    }

    mapped_params = {
        entry["official_param"]
        for entry in localization["agent_param_mapping"]
        if entry["official_param"] is not None
    }
    assert {
        "additional_fasta",
        "bbsplit_fasta_list",
        "fasta",
        "gff",
        "gtf",
        "hisat2_index",
        "input",
        "pseudo_aligner",
        "salmon_index",
        "skip_bbsplit",
        "transcript_fasta",
        "umitools_bc_pattern",
    }.issubset(mapped_params)

    ignored_fields = {entry["config_field"] for entry in localization["ignored_upstream_params"]}
    assert ignored_fields == {
        "aws.client.anonymous",
        "params.hisat2_build_memory",
        "params.modules_testdata_base_path",
        "params.outdir",
        "params.pipelines_testdata_base_path",
        "process.withName:'.*'",
        "process.withName:'FASTQ_QC_TRIM_FILTER_SETSTRANDEDNESS:FQ_LINT_AFTER_SORTMERNA'",
    }

    assert contract["launch"]["config_files"] == [
        "/data/rnaseq_test_data/project-files/pipeline-support-rnaseq/profile_test_overrides.config"
    ]
    assert contract["launch"]["config_files"] == [
        item["path"] for item in contract["launch"]["config_overrides"]
    ]
    assert localization["config_override_files"][0]["path"] == contract["launch"]["config_files"][0]
    assert "cpus  : 4" in localization["config_override_files"][0]["content"]
    assert "memory: '15.GB'" in localization["config_override_files"][0]["content"]
    assert "time  : '1.h'" in localization["config_override_files"][0]["content"]
    assert (
        'ext.args2 = "--genomeSAindexNbases 7"'
        in localization["config_override_files"][0]["content"]
    )

    required_paths = set(contract["assertions"]["artifacts"]["required_paths"])
    assert required_paths == {
        "custom/out/genome_gfp.gtf",
        "multiqc/star_salmon/multiqc_report.html",
        "salmon/salmon.merged.gene.SummarizedExperiment.rds",
        "star_salmon/RAP1_IAA_30M_REP1.markdup.sorted.bam",
        "star_salmon/salmon.merged.gene.SummarizedExperiment.rds",
    }

    assert_brief_is_client_visible(brief)
    assert "prepared local dataset" in brief
    assert_brief_uses_expected_project_names(brief, "rnaseq")
    assert "/data/rnaseq_test_data/samplesheet_test_local.csv" in brief
    assert "/data/analysis/pipeline-support" not in brief
    assert "STAR + Salmon" in brief
    assert "BBSplit enabled" in brief
    assert "Kallisto" not in brief
    assert "STAR-RSEM" not in brief
    assert "BAM-input" not in brief
    assert_brief_mentions_resource_caps(brief, cpus=4, memory="15.GB", runtime="1.h")
    assert "genomeSAindexNbases 7" not in brief
    assert "profile_test_overrides.config" not in brief
    assert script_path.is_file()


def test_riboseq_smoke_support_files_are_consistent() -> None:
    case_dir = CONTRACT_ROOT / "riboseq"
    contract_path = case_dir / "smoke.yaml"
    localization_path = case_dir / "smoke.localization.yaml"
    script_path = case_dir / "localize_testdata.py"

    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    localization = yaml.safe_load(localization_path.read_text(encoding="utf-8"))
    brief = read_prompt_brief(case_dir, contract)

    assert localization["kind"] == "pipeline_test_localization"
    assert localization["pipeline"] == contract["pipeline"]
    assert localization["case_id"] == contract["case_id"]
    assert localization["localized_root"] == contract["local_data_contract"]["localized_root"]
    assert localization["localized_root"] == "/data/nextmcp/testdata/riboseq/test"

    expected_paths = {
        entry["expected_path"] for entry in contract["local_data_contract"]["rewritten_manifests"]
    }
    localized_paths = {entry["localized_path"] for entry in localization["rewritten_manifests"]}
    assert localized_paths == expected_paths
    assert contract["launch"]["params"]["input"] in localized_paths
    assert contract["launch"]["params"]["ribo_database_manifest"] in localized_paths

    url_roles = {entry["role"] for entry in localization["url_inventory"]}
    assert url_roles == {
        "input_samplesheet",
        "contrasts_table",
        "ribo_database_manifest",
        "genome_fasta",
        "annotation_gtf",
    }

    mapped_params = {
        entry["official_param"]
        for entry in localization["agent_param_mapping"]
        if entry["official_param"] is not None
    }
    assert {
        "input",
        "contrasts",
        "ribo_database_manifest",
        "fasta",
        "gtf",
        "min_trimmed_reads",
        "skip_ribotricer",
        "aligner",
    }.issubset(mapped_params)

    ignored_fields = {entry["config_field"] for entry in localization["ignored_upstream_params"]}
    assert ignored_fields == {
        "params.outdir",
        "params.test_data_base",
        "params.modules_testdata_base_path",
        "params.extra_fqlint_args",
        "process.withName:'.*'",
        "process.withName:'FQ_SUBSAMPLE'",
        "process.withName:'GFFREAD'",
        "includeConfig:https://raw.githubusercontent.com/nf-core/modules/0094ae45ba8f5a2e30644d4e252970775a03ee91/tests/config/test_data.config",
    }

    assert contract["classification"]["primary_mode"] == "profile-only"
    assert contract["classification"]["modifiers"] == [
        "localize-remote-inputs",
        "snapshot-rich",
    ]
    assert contract["launch"]["params"]["contrasts"] == (
        "/data/nextmcp/testdata/riboseq/test/pipeline-data/riboseq/contrasts.csv"
    )
    assert contract["launch"]["params"]["fasta"] == (
        "/data/nextmcp/testdata/riboseq/test/pipeline-data/modules/data/genomics/"
        "homo_sapiens/riboseq_expression/Homo_sapiens.GRCh38.dna.chromosome.20.fa.gz"
    )
    assert contract["launch"]["config_files"] == [
        "/data/nextmcp/testdata/riboseq/test/project-files/pipeline-support-riboseq/profile_test_overrides.config"
    ]
    assert contract["launch"]["config_files"] == [
        item["path"] for item in contract["launch"]["config_overrides"]
    ]
    assert localization["config_override_files"][0]["path"] == contract["launch"]["config_files"][0]
    assert "cpus: 4" in localization["config_override_files"][0]["content"]
    assert "memory: '15.GB'" in localization["config_override_files"][0]["content"]
    assert "time: '1.h'" in localization["config_override_files"][0]["content"]

    required_paths = set(contract["assertions"]["artifacts"]["required_paths"])
    assert required_paths == {
        "alignment/star/sorted/SRX11780879.genome.sorted.bam",
        "multiqc/star/multiqc_report.html",
        "quantification/salmon/salmon.merged.gene_counts.tsv",
        "riboseq_qc/ribotish/SRX11780885_qual.txt",
        "translational_efficiency/anota2seq/treated_vs_control.translation.anota2seq.results.tsv",
    }

    content_checks = {
        entry["path"]: entry["expected"]
        for entry in contract["assertions"]["artifacts"]["content_checks"]
    }
    assert content_checks == {
        "alignment/star/log/SRX11780879.SJ.out.tab": "b5239565ecf18cd55147a4e67d7db3a2",
        "alignment/star/sorted/samtools_stats/SRX11780879.genome.sorted.bam.idxstats": (
            "b0e56d0944762d792ed9de03b467f960"
        ),
    }

    assert_brief_is_client_visible(brief)
    assert_brief_uses_expected_project_names(brief, "riboseq")
    assert (
        "/data/nextmcp/testdata/riboseq/test/rewrites/pipeline-data/riboseq/samplesheet/samplesheet_local.csv"
        in brief
    )
    assert "/data/analysis/pipeline-support" not in brief
    assert "/data/nextmcp/testdata/riboseq/test/pipeline-data/riboseq/contrasts.csv" in brief
    assert "Ribo-TISH" in brief
    assert "translational-efficiency" in brief
    assert "Ribotricer" in brief
    assert "tests/main.nf.test" not in brief
    assert "production" not in brief
    assert_brief_mentions_resource_caps(brief, cpus=4, memory="15.GB", runtime="1.h")
    assert contract["prompt_brief"].split() == brief.split()
    assert localization["natural_language_execution_brief"].split() == brief.split()
    assert script_path.is_file()


def test_rnafusion_smoke_support_files_are_consistent() -> None:
    case_dir = CONTRACT_ROOT / "rnafusion"
    contract_path = case_dir / "smoke.yaml"
    localization_path = case_dir / "smoke.localization.yaml"
    script_path = case_dir / "localize_testdata.py"

    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    localization = yaml.safe_load(localization_path.read_text(encoding="utf-8"))
    brief = read_prompt_brief(case_dir, contract)

    assert contract["mode"] == "profile-only"
    assert contract["classification"]["primary_mode"] == "profile-only"
    assert set(contract["classification"]["modifiers"]) == {
        "environment-sensitive",
        "localize-remote-inputs",
        "snapshot-rich",
    }

    assert localization["kind"] == "pipeline_test_localization"
    assert localization["pipeline"] == contract["pipeline"]
    assert localization["case_id"] == contract["case_id"]
    assert localization["localized_root"] == contract["local_data_contract"]["localized_root"]

    rewritten_manifest = localization["rewritten_manifests"][0]
    expected_path = contract["local_data_contract"]["rewritten_manifests"][0]["expected_path"]
    assert rewritten_manifest["localized_path"] == expected_path
    assert contract["launch"]["params"]["input"] == expected_path

    refs_prefix = "/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/refs/heads/rnafusion/"
    for field in (
        "dfam_hmm",
        "dfam_h3f",
        "dfam_h3i",
        "dfam_h3m",
        "dfam_h3p",
        "pfam_file",
        "arriba_ref_protein_domains",
        "arriba_ref_known_fusions",
        "arriba_ref_blacklist",
        "arriba_ref_cytobands",
    ):
        assert contract["launch"]["params"][field].startswith(refs_prefix)
    assert "annot_filter_url" not in contract["launch"]["params"]

    url_roles = {entry["role"] for entry in localization["url_inventory"]}
    assert url_roles == {
        "fastq_read_1",
        "fastq_read_2",
        "minigenome_fasta",
        "minigenome_gtf",
        "fusion_annot_lib",
        "dfam_hmm",
        "dfam_h3f",
        "dfam_h3i",
        "dfam_h3m",
        "dfam_h3p",
        "pfam_file",
        "arriba_ref_blacklist",
        "arriba_ref_cytobands",
        "arriba_ref_known_fusions",
        "arriba_ref_protein_domains",
    }

    mapped_params = {
        entry["official_param"]
        for entry in localization["agent_param_mapping"]
        if entry["official_param"] is not None
    }
    assert {
        "input",
        "references_only",
        "tools",
        "no_cosmic",
        "genome",
        "genome_gencode_version",
        "species",
        "fasta",
        "gtf",
        "fusion_annot_lib",
        "dfam_hmm",
        "dfam_h3f",
        "dfam_h3i",
        "dfam_h3m",
        "dfam_h3p",
        "pfam_file",
        "arriba_ref_protein_domains",
        "arriba_ref_known_fusions",
        "arriba_ref_blacklist",
        "arriba_ref_cytobands",
        "fusionreport_ref",
    }.issubset(mapped_params)

    resolved_params = set(localization["source_profile"]["resolved_params"])
    assert mapped_params.issubset(resolved_params | {"references_only", "tools"})

    ignored_fields = {entry["config_field"] for entry in localization["ignored_upstream_params"]}
    assert ignored_fields == {
        "nextflow.config:params.input",
        "nextflow.config:params.genomes_base",
        "nextflow.config:params.fusioncatcher_ref",
        "tests/nextflow.config:params.modules_testdata_base_path",
        "tests/nextflow.config:params.pipelines_testdata_base_path",
        "tests/nextflow.config:params.dfam_hmm",
        "tests/nextflow.config:params.dfam_h3f",
        "tests/nextflow.config:params.dfam_h3i",
        "tests/nextflow.config:params.dfam_h3m",
        "tests/nextflow.config:params.dfam_h3p",
        "tests/nextflow.config:params.pfam_file",
        "tests/nextflow.config:params.arriba_ref_blacklist",
        "tests/nextflow.config:params.arriba_ref_cytobands",
        "tests/nextflow.config:params.arriba_ref_known_fusions",
        "tests/nextflow.config:params.arriba_ref_protein_domains",
        "aws.client.anonymous",
        "params.outdir",
    }

    assert contract["launch"]["config_files"] == [
        "/data/nextmcp/testdata/rnafusion/test_build/project-files/pipeline-support-rnafusion/profile_test_build_overrides.config"
    ]
    assert contract["launch"]["config_files"] == [
        item["path"] for item in contract["launch"]["config_overrides"]
    ]
    assert localization["config_override_files"][0]["path"] == contract["launch"]["config_files"][0]
    override_content = localization["config_override_files"][0]["content"]
    assert 'genomes_base = "${params.outdir}/references"' in override_content
    assert "cpus: 4" in override_content
    assert "memory: '15.GB'" in override_content
    assert "time: '1.h'" in override_content

    prepare_required_paths = set(contract["assertions"]["prepare"]["required_paths"])
    assert {
        "/data/nextmcp/testdata/rnafusion/test_build/repo-assets/tests/csv/fastq.csv",
        "/data/nextmcp/testdata/rnafusion/test_build/rewrites/repo-assets/tests/csv/fastq_local.csv",
        (
            "/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/"
            "81cb45949e75cbb85cbf6c5ec9009ab45b160823/testdata/human/reads_1.fq.gz"
        ),
        (
            "/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/"
            "81cb45949e75cbb85cbf6c5ec9009ab45b160823/testdata/human/reads_2.fq.gz"
        ),
        "/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/refs/heads/rnafusion/testdata/human/test_starfusion_dfam.hmm",
        "/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/refs/heads/rnafusion/testdata/human/Pfam-A.hmm.gz",
        (
            "/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/refs/heads/rnafusion/"
            "testdata/reference/arriba/protein_domains_hg38_GRCh38_v2.5.0.gff3"
        ),
        "/data/nextmcp/testdata/rnafusion/test_build/inputs/fusion_report_db/fusiongdb2.db",
        "/data/nextmcp/testdata/rnafusion/test_build/inputs/fusion_report_db/mitelman.db",
        "/data/nextmcp/testdata/rnafusion/test_build/inputs/fusion_report_db/DB-timestamp.txt",
    }.issubset(prepare_required_paths)
    assert (
        "/data/nextmcp/testdata/rnafusion/test_build/inputs/hgnc/HGNC-DB-timestamp.txt"
        not in prepare_required_paths
    )

    assert "hgnc_ref" not in contract["launch"]["params"]
    assert "hgnc_date" not in contract["launch"]["params"]
    assert (
        contract["launch"]["params"]["fusionreport_ref"]
        == "/data/nextmcp/testdata/rnafusion/test_build/inputs/fusion_report_db"
    )
    assert localization["generated_file_inventory"] == [
        {
            "role": "fusionreport_ref",
            "source_requirement": (
                "Reuse an existing local `fusion_report_db` directory, copy one supplied "
                "with `--fusionreport-db`, or build it with `fusion_report download "
                "--no-cosmic`."
            ),
            "localized_path": "/data/nextmcp/testdata/rnafusion/test_build/inputs/fusion_report_db",
        }
    ]

    assert_brief_is_client_visible(brief)
    assert_brief_uses_expected_project_names(brief, "rnafusion")
    assert "/data/analysis/pipeline-support" not in brief
    assert (
        "/data/nextmcp/testdata/rnafusion/test_build/pipeline-data/refs/heads/rnafusion/"
        "testdata/reference/arriba"
    ) in brief
    assert "CTAT_HumanFusionLib.mini.dat.gz" in brief
    assert "AnnotFilterRule.pm" not in brief
    assert "annot_filter_url" not in brief
    assert "fastq_local.csv" in brief
    assert "FASTQ bundle root" in brief
    assert "HGNC reference root" not in brief
    assert "FusionReport database root" in brief
    assert (
        "/data/nextmcp/testdata/rnafusion/test_build/downloads/data.broadinstitute.org/"
        "Trinity/CTAT_RESOURCE_LIB/AnnotFilterRule.pm"
    ) not in brief
    assert (
        "https://data.broadinstitute.org/Trinity/CTAT_RESOURCE_LIB/AnnotFilterRule.pm" not in brief
    )
    assert "Pfam-A.hmm.gz" in brief
    assert "DFAM HMM" in brief
    assert "workflow create HGNC reference data during the run" in brief
    assert_brief_mentions_resource_caps(brief, cpus=4, memory="15.GB", runtime="1.h")
    assert contract["prompt_brief"].split() == brief.split()
    assert localization["natural_language_execution_brief"].split() == brief.split()
    assert script_path.is_file()
