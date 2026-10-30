"""Tests for nextmcp.tools.nextflow_tools."""

from __future__ import annotations

import json
import stat
import sys
from pathlib import Path
from typing import Any

from nextmcp.config import (
    AppConfig,
    AuthConfig,
    NextflowConfig,
    PathsConfig,
    ServerConfig,
    StateConfig,
)
from nextmcp.runtime_state import RuntimeState
from nextmcp.tools.capability_tools import register_capability_tools
from nextmcp.tools.fs_tools import register_fs_tools
from nextmcp.tools.nextflow_tools import register_nextflow_tools
from nextmcp.tools.project_tools import register_project_tools
from nextmcp.tools.run_tools import register_run_tools
from tests.conftest import assert_tool_error, registered_tool_functions

SESSION_UUID = "0056928b-dc55-41fe-a16f-3923983001da"


def test_nextflow_run_builds_expected_project_scoped_command(tmp_path: Path) -> None:
    tools = _build_toolset(tmp_path)
    nextflow_run = tools["nextflow_run"]
    run_get = tools["run_get"]
    run_list = tools["run_list"]
    run_logs = tools["run_logs"]

    project = "analysis-1"
    project_root = _project_root(tmp_path, project)
    project_root.mkdir(parents=True)
    (project_root / "samples.csv").write_text("sample,fastq_1\n", encoding="utf-8")
    (project_root / "relative.config").write_text("params.bar = 'baz'\n", encoding="utf-8")
    absolute_config = tmp_path / "absolute.config"
    absolute_config.write_text("params.foo = 'bar'\n", encoding="utf-8")

    result = nextflow_run(
        pipeline="rnaseq",
        project=project,
        run_name="nf-local",
        entry="main",
        params={
            "input": "samples.csv",
            "threads": 4,
            "enabled": True,
            "skip": None,
        },
        profile="test,docker",
        config_files=[str(absolute_config), "relative.config"],
        extra_args=["-with-report", "report.html"],
        env={"NF_SHARED": "override", "NF_ONLY": "yes"},
        detach=False,
    )

    assert result["ok"] is True
    assert result["project_id"] == project
    assert result["run_name"] == "nf-local"
    assert result["status"] == "succeeded"
    assert result["entry"] == "main"
    assert result["profile"] == "test,docker"
    assert "process_id" not in result

    run_id = str(result["run_id"])
    full_record = run_get(run_id, detail="full")
    run_root = project_root / "runs" / run_id
    results_dir = project_root / "results" / run_id

    assert full_record["ok"] is True
    assert full_record["project_root"] == str(project_root.resolve())
    assert full_record["run_root"] == str(run_root.resolve())
    assert full_record["results_dir"] == str(results_dir.resolve())
    assert full_record["work_dir"] == str((run_root / "work").resolve())
    assert full_record["job_dir"] == str((run_root / "job").resolve())
    assert full_record["config_files"] == [
        str(absolute_config.resolve()),
        str((project_root / "relative.config").resolve()),
    ]
    assert full_record["resume"] is False
    assert full_record["resume_session_id"] is None
    assert full_record["extra_args"] == ["-with-report", "report.html"]
    assert full_record["run_layout"] == {
        "run_root": str(run_root.resolve()),
        "work_dir": str((run_root / "work").resolve()),
        "work_dir_source": "explicit",
        "results_dir": str(results_dir.resolve()),
        "results_dir_source": "params.outdir",
        "job_dir": str((run_root / "job").resolve()),
    }
    assert full_record["layout_warnings"] == []
    assert full_record["pipeline_fingerprint"]["mode"] == "local"
    assert full_record["pipeline_fingerprint"]["target"] == "rnaseq"
    assert full_record["pipeline_fingerprint"]["digest"].startswith("sha256:")
    assert isinstance(full_record["process_id"], str)

    important = run_logs(run_id)
    assert important["view"] == "important"
    assert important["stream"] == "nextflow"
    assert important["path"] == full_record["nextflow_log"]
    assert important["category"] == "succeeded"
    assert important["summary"] == "Nextflow run finished successfully."
    assert important["important_lines"] == ["fake nextflow log"]
    assert important["evidence"] == [
        {
            "source": "nextflow_log",
            "path": full_record["nextflow_log"],
            "lines": ["fake nextflow log"],
        }
    ]

    stdout = run_logs(run_id, stream="stdout", view="raw")
    stdout_payload = json.loads(stdout["content"])
    argv = stdout_payload["argv"]
    nextflow_logs = run_logs(run_id, stream="nextflow", view="raw")

    assert nextflow_logs["path"] == full_record["nextflow_log"]
    assert nextflow_logs["content"] == f"Session UUID: {SESSION_UUID}\nfake nextflow log\n"
    assert nextflow_logs["stream"] == "nextflow"

    assert argv[:4] == [
        "-log",
        full_record["nextflow_log"],
        "run",
        "<pipeline_materials_redacted>",
    ]
    assert str(tmp_path / "pipelines") not in stdout["content"]
    assert_subsequence(argv, ["-entry", "main"])
    assert_subsequence(argv, ["-profile", "test,docker"])
    assert_subsequence(argv, ["-c", str(absolute_config.resolve())])
    assert_subsequence(argv, ["-c", str((project_root / "relative.config").resolve())])
    assert_subsequence(argv, ["-work-dir", str((run_root / "work").resolve())])
    assert "-resume" not in argv
    assert_subsequence(argv, ["--input", str((project_root / "samples.csv").resolve())])
    assert_subsequence(argv, ["--outdir", str(results_dir.resolve())])
    assert_subsequence(argv, ["--threads", "4"])
    assert_subsequence(argv, ["--enabled", "true"])
    assert "--skip" not in argv
    assert_subsequence(argv, ["-with-report", "report.html"])

    env_payload = stdout_payload["env"]
    assert env_payload["NXF_HOME"] == "/tmp/fake-nxf-home"
    assert env_payload["NF_SHARED"] == "override"
    assert env_payload["NF_ONLY"] == "yes"

    listing = run_list(project=project, detail="full")
    assert listing["count"] == 1
    assert listing["runs"][0]["run_id"] == run_id
    assert listing["runs"][0]["results_dir"] == str(results_dir.resolve())


def test_nextflow_run_accepts_single_config_file_string(tmp_path: Path) -> None:
    tools = _build_toolset(tmp_path)
    nextflow_run = tools["nextflow_run"]
    run_get = tools["run_get"]
    run_logs = tools["run_logs"]

    project = "single-config-demo"
    project_root = _project_root(tmp_path, project)
    project_root.mkdir(parents=True)
    (project_root / "samples.csv").write_text("sample,fastq_1\n", encoding="utf-8")
    (project_root / "relative.config").write_text("params.foo = 'bar'\n", encoding="utf-8")

    result = nextflow_run(
        pipeline="rnaseq",
        project=project,
        params={"input": "samples.csv"},
        config_files="relative.config",
        detach=False,
    )

    assert result["ok"] is True

    run_id = str(result["run_id"])
    full_record = run_get(run_id, detail="full")
    assert full_record["config_files"] == [str((project_root / "relative.config").resolve())]

    stdout = run_logs(run_id, stream="stdout", view="raw")
    argv = json.loads(stdout["content"])["argv"]
    assert_subsequence(argv, ["-c", str((project_root / "relative.config").resolve())])


def test_nextflow_run_does_not_resolve_numeric_string_params_as_paths(
    tmp_path: Path,
) -> None:
    tools = _build_toolset(tmp_path)
    nextflow_run = tools["nextflow_run"]
    run_get = tools["run_get"]

    project = "numeric-param-demo"
    project_root = _project_root(tmp_path, project)
    project_root.mkdir(parents=True)
    (project_root / "samples.csv").write_text("sample,fastq_1\n", encoding="utf-8")

    prepared = nextflow_run(
        pipeline="rnaseq",
        project=project,
        params={
            "input": "samples.csv",
            "gtdbtk_min_completeness": "0.01",
            "negative_threshold": "-1.5",
        },
        prepare=True,
    )

    assert prepared["ok"] is True
    run_id = str(prepared["run"]["run_id"])

    full_record = run_get(run_id, detail="full")
    assert full_record["params"]["input"] == str((project_root / "samples.csv").resolve())
    assert full_record["params"]["gtdbtk_min_completeness"] == "0.01"
    assert full_record["params"]["negative_threshold"] == "-1.5"
    assert not any(
        item["param"] in {"gtdbtk_min_completeness", "negative_threshold"}
        for item in prepared["path_checks"]
    )


def test_nextflow_run_keeps_remote_pipeline_id(tmp_path: Path) -> None:
    tools = _build_toolset(tmp_path)
    nextflow_run = tools["nextflow_run"]
    run_get = tools["run_get"]
    run_logs = tools["run_logs"]

    project = "remote-demo"
    result = nextflow_run(
        pipeline="nf-core/rnaseq",
        project=project,
        detach=False,
    )

    assert result["ok"] is True
    assert result["status"] == "succeeded"
    assert result["pipeline"] == "nf-core/rnaseq"
    assert result["profile"] == "docker"

    run_id = str(result["run_id"])
    full_record = run_get(run_id, detail="full")
    project_root = _project_root(tmp_path, project)
    run_root = project_root / "runs" / run_id
    results_dir = project_root / "results" / run_id

    assert full_record["resume"] is False
    assert full_record["resume_session_id"] is None
    assert full_record["config_files"] == []
    assert full_record["work_dir"] == str((run_root / "work").resolve())
    assert full_record["results_dir"] == str(results_dir.resolve())
    assert full_record["run_layout"] == {
        "run_root": str(run_root.resolve()),
        "work_dir": str((run_root / "work").resolve()),
        "work_dir_source": "explicit",
        "results_dir": str(results_dir.resolve()),
        "results_dir_source": "project.default",
        "job_dir": str((run_root / "job").resolve()),
    }
    assert [item["kind"] for item in full_record["layout_warnings"]] == [
        "primary_results_dir_unbound"
    ]
    assert full_record["pipeline_fingerprint"] == {
        "mode": "remote_unpinned",
        "target": "nf-core/rnaseq",
        "digest": None,
    }

    stdout = run_logs(run_id, stream="stdout", view="raw")
    argv = json.loads(stdout["content"])["argv"]
    assert argv[:4] == [
        "-log",
        full_record["nextflow_log"],
        "run",
        "nf-core/rnaseq",
    ]
    assert_subsequence(argv, ["-profile", "docker"])
    assert "-resume" not in argv


def test_nextflow_run_supplies_igenomes_override_as_config(tmp_path: Path) -> None:
    tools = _build_toolset(tmp_path, igenomes_ignore=True)
    nextflow_run = tools["nextflow_run"]
    run_logs = tools["run_logs"]

    project = "igenome-demo"
    project_root = _project_root(tmp_path, project)
    project_root.mkdir(parents=True)
    (project_root / "samples.csv").write_text("sample,fastq_1\n", encoding="utf-8")

    result = nextflow_run(
        pipeline="rnaseq",
        project=project,
        params={
            "input": "samples.csv",
            "igenomes_ignore": False,
            "igenomes_base": "/custom/igenome",
        },
        detach=False,
    )

    assert result["ok"] is True

    stdout = run_logs(str(result["run_id"]), stream="stdout", view="raw")
    argv = json.loads(stdout["content"])["argv"]
    assert "--igenomes_ignore" not in argv
    assert "--igenomes_base" not in argv
    config_paths = [argv[index + 1] for index, value in enumerate(argv) if value == "-c"]
    override_paths = [
        Path(value) for value in config_paths if value.endswith("nextmcp-igenomes.config")
    ]
    assert len(override_paths) == 1
    content = override_paths[0].read_text(encoding="utf-8")
    assert "igenomes_ignore = true" in content
    assert "igenomes_base = '/tmp/igenome_tmp'" in content
    assert "/custom/igenome" not in argv


def test_nextflow_run_prepare_mode_returns_project_scoped_launch_plan(tmp_path: Path) -> None:
    tools = _build_toolset(tmp_path)
    nextflow_run = tools["nextflow_run"]
    run_get = tools["run_get"]
    run_list = tools["run_list"]

    project = "prepare-demo"
    project_root = _project_root(tmp_path, project)
    project_root.mkdir(parents=True)
    (project_root / "samples.csv").write_text("sample,fastq_1\n", encoding="utf-8")

    prepared = nextflow_run(
        pipeline="rnaseq",
        project=project,
        params={"input": "samples.csv"},
        prepare=True,
    )

    assert prepared["ok"] is True
    assert prepared["kind"] == "nextflow"
    assert prepared["mode"] == "prepare"
    assert prepared["project"] == {
        "project_id": project,
        "project_root": str(project_root.resolve()),
        "created": False,
    }
    assert prepared["run"]["project_id"] == project
    assert prepared["run"]["status"] == "prepared"
    assert prepared["layout_warnings"] == []

    run_id = str(prepared["run"]["run_id"])
    expected_run_root = project_root / "runs" / run_id
    assert prepared["run_layout"] == {
        "run_root": str(expected_run_root.resolve()),
        "work_dir": str((expected_run_root / "work").resolve()),
        "work_dir_source": "explicit",
        "results_dir": str((project_root / "results" / run_id).resolve()),
        "results_dir_source": "params.outdir",
        "job_dir": str((expected_run_root / "job").resolve()),
    }

    listing = run_list(project=project)
    assert listing["count"] == 1
    assert listing["runs"][0]["run_id"] == run_id
    assert listing["runs"][0]["status"] == "prepared"

    prepared_run = run_get(run_id, detail="full")
    assert prepared_run["status"] == "prepared"
    assert prepared_run["process_id"] is None
    assert prepared_run["launch_spec"]["pipeline"] == "rnaseq"
    assert prepared_run["resume_compatible"] is False
    assert prepared_run["resume_incompatible_reason"] == (
        "The run has not started yet, so no Nextflow session exists."
    )


def test_run_get_full_exposes_launch_spec_and_resume_metadata(tmp_path: Path) -> None:
    tools = _build_toolset(tmp_path)
    nextflow_run = tools["nextflow_run"]
    run_get = tools["run_get"]

    project = "resume-meta-demo"
    project_root = _project_root(tmp_path, project)
    project_root.mkdir(parents=True)
    (project_root / "samples.csv").write_text("sample,fastq_1\n", encoding="utf-8")

    result = nextflow_run(
        pipeline="rnaseq",
        project=project,
        params={"input": "samples.csv", "threads": 4},
        detach=False,
    )

    full_record = run_get(str(result["run_id"]), detail="full")
    assert full_record["nextflow_session_uuid"] == SESSION_UUID
    assert full_record["resume_compatible"] is True
    assert full_record["resume_requires_same_run_root"] is True
    assert full_record["resume_requires_same_work_dir"] is True
    assert full_record["launch_spec"] == {
        "pipeline": "rnaseq",
        "entry": None,
        "profile": "docker",
        "config_files": [],
        "params": {
            "input": str((project_root / "samples.csv").resolve()),
            "outdir": full_record["results_dir"],
            "threads": "4",
        },
        "extra_args": [],
    }


def test_prepare_from_run_id_reports_resume_plan(tmp_path: Path) -> None:
    tools = _build_toolset(tmp_path)
    nextflow_run = tools["nextflow_run"]

    project = "resume-prepare-demo"
    project_root = _project_root(tmp_path, project)
    project_root.mkdir(parents=True)
    (project_root / "samples.csv").write_text("sample,fastq_1\n", encoding="utf-8")

    first = nextflow_run(
        pipeline="rnaseq",
        project=project,
        run_id="attempt6",
        params={"input": "samples.csv"},
        detach=False,
    )
    assert first["ok"] is True

    prepared = nextflow_run(
        from_run_id="attempt6",
        prepare=True,
    )
    hint = prepared["resume_hint"]
    assert hint["requested"] is True
    assert hint["can_try_resume"] is True
    assert hint["source_run_id"] == "attempt6"
    assert hint["resume_requires_same_run_root"] is True
    assert hint["resume_requires_same_work_dir"] is True
    assert hint["resume_incompatible_reason"] is None
    assert hint["existing_job_dir"] == str(project_root / "runs" / "attempt6" / "job")
    assert hint["job_dir_archive_on_launch"] is True


def test_nextflow_run_from_run_id_reuses_launch_spec_and_archives_previous_job_dir(
    tmp_path: Path,
) -> None:
    tools = _build_toolset(tmp_path)
    nextflow_run = tools["nextflow_run"]
    run_get = tools["run_get"]
    run_logs = tools["run_logs"]

    project = "resume-run-demo"
    project_root = _project_root(tmp_path, project)
    project_root.mkdir(parents=True)
    (project_root / "samples.csv").write_text("sample,fastq_1\n", encoding="utf-8")
    (project_root / "base.config").write_text("params.foo = 'base'\n", encoding="utf-8")
    (project_root / "override.config").write_text("params.foo = 'override'\n", encoding="utf-8")

    nextflow_run(
        pipeline="rnaseq",
        project=project,
        run_id="attempt6",
        params={"input": "samples.csv", "threads": 4},
        config_files="base.config",
        detach=False,
    )
    first_full = run_get("attempt6", detail="full")
    (Path(first_full["job_dir"]) / "marker.txt").write_text("old job\n", encoding="utf-8")

    resumed = nextflow_run(
        from_run_id="attempt6",
        config_files="override.config",
        params={"threads": 8},
        detach=False,
    )

    assert resumed["ok"] is True
    assert resumed["run_id"] == "attempt6"

    full_record = run_get("attempt6", detail="full")
    assert full_record["config_files"] == [str((project_root / "override.config").resolve())]
    assert full_record["params"] == {
        "input": str((project_root / "samples.csv").resolve()),
        "outdir": full_record["results_dir"],
        "threads": "8",
    }
    assert full_record["resume_source_run_id"] == "attempt6"
    assert isinstance(full_record["archived_job_dir"], str)
    archived_job_dir = Path(full_record["archived_job_dir"])
    assert archived_job_dir.exists()
    assert (archived_job_dir / "marker.txt").read_text(encoding="utf-8") == "old job\n"

    stdout = run_logs("attempt6", stream="stdout", view="raw")
    argv = json.loads(stdout["content"])["argv"]
    assert_subsequence(argv, ["-resume", SESSION_UUID])
    assert_subsequence(argv, ["-c", str((project_root / "override.config").resolve())])
    assert_subsequence(argv, ["--threads", "8"])
    assert_subsequence(argv, ["--input", str((project_root / "samples.csv").resolve())])
    assert str((project_root / "base.config").resolve()) not in argv


def test_nextflow_run_from_run_id_rejects_manual_layout_fields(
    tmp_path: Path,
) -> None:
    tools = _build_toolset(tmp_path)
    nextflow_run = tools["nextflow_run"]

    project = "source-match-demo"
    project_root = _project_root(tmp_path, project)
    project_root.mkdir(parents=True)
    (project_root / "samples.csv").write_text("sample,fastq_1\n", encoding="utf-8")

    nextflow_run(
        pipeline="rnaseq",
        project=project,
        run_id="attempt6",
        params={"input": "samples.csv"},
        detach=False,
    )

    project_error = assert_tool_error(
        nextflow_run(
            from_run_id="attempt6",
            project="other-project",
            detach=False,
        ),
        "invalid_arguments",
    )
    assert "do not pass `project`" in str(project_error["message"])

    pipeline_error = assert_tool_error(
        nextflow_run(
            from_run_id="attempt6",
            pipeline="nf-core/rnaseq",
            detach=False,
        ),
        "invalid_arguments",
    )
    assert "do not pass `pipeline`" in str(pipeline_error["message"])

    run_id_error = assert_tool_error(
        nextflow_run(
            from_run_id="attempt6",
            run_id="attempt7",
            detach=False,
        ),
        "invalid_arguments",
    )
    assert "do not pass `run_id`" in str(run_id_error["message"])


def test_run_logs_important_nextflow_failure_reads_task_command_err(tmp_path: Path) -> None:
    tools = _build_toolset(tmp_path, fake_mode="task_failure")
    nextflow_run = tools["nextflow_run"]
    run_logs = tools["run_logs"]

    project = "failure-demo"
    project_root = _project_root(tmp_path, project)
    project_root.mkdir(parents=True)
    (project_root / "samples.csv").write_text("sample,fastq_1\n", encoding="utf-8")

    result = nextflow_run(
        pipeline="rnaseq",
        project=project,
        params={"input": "samples.csv"},
        detach=False,
    )

    assert result["ok"] is True
    assert result["status"] == "failed"

    run_id = str(result["run_id"])
    important = run_logs(run_id)
    assert important["view"] == "important"
    assert important["stream"] == "nextflow"
    assert important["category"] == "task_failure"
    assert important["summary"] == "Task failed inside process ALIGN_READS (sample1)."
    assert any(
        item["source"] == "task_command_err"
        and item["lines"] == ["/bin/bash: salmon: command not found"]
        for item in important["evidence"]
    )
    assert (
        "ERROR ~ Error executing process > 'ALIGN_READS (sample1)'" in important["important_lines"]
    )
    assert "/bin/bash: salmon: command not found" in important["important_lines"]

    raw = run_logs(run_id, view="raw")
    assert "Error executing process > 'ALIGN_READS (sample1)'" in raw["content"]


def test_nextflow_run_exposes_run_artifacts_and_project_filters(tmp_path: Path) -> None:
    tools = _build_toolset(tmp_path)
    nextflow_run = tools["nextflow_run"]
    project_get = tools["project_get"]
    run_artifacts = tools["run_artifacts"]
    run_get = tools["run_get"]
    run_list = tools["run_list"]

    project = "artifact-demo"
    project_root = _project_root(tmp_path, project)
    project_root.mkdir(parents=True)
    (project_root / "samples.csv").write_text("sample,fastq_1\n", encoding="utf-8")

    result = nextflow_run(
        pipeline="rnaseq",
        project=project,
        params={"input": "samples.csv"},
        extra_args=["-with-report", "report.html"],
        detach=False,
    )

    run_id = str(result["run_id"])
    full_record = run_get(run_id, detail="full")

    declared_outputs = run_artifacts(run_id, section="declared_outputs")
    published_roots = run_artifacts(run_id, section="published_roots")
    items = run_artifacts(run_id, section="items", detail="full")

    assert declared_outputs["ok"] is True
    assert declared_outputs["run_id"] == run_id
    assert published_roots["ok"] is True
    assert items["ok"] is True
    assert any(item.get("path") == full_record["results_dir"] for item in declared_outputs["items"])
    assert any(item.get("path") == full_record["results_dir"] for item in published_roots["items"])
    assert any(str(item.get("path", "")).endswith("summary.txt") for item in items["items"])
    pipeline_root = str((tmp_path / "pipelines").resolve())
    assert pipeline_root not in json.dumps(declared_outputs)
    assert pipeline_root not in json.dumps(published_roots)
    assert pipeline_root not in json.dumps(items)

    filtered = run_list(project=project, artifact_path_contains="summary.txt")
    assert filtered["count"] == 1
    assert filtered["runs"][0]["run_id"] == run_id

    project_payload = project_get(project, detail="full")
    assert project_payload["project_id"] == project
    assert project_payload["run_count"] == 1
    assert project_payload["runs"][0]["run_id"] == run_id


def test_hidden_pipeline_materials_still_allow_schema_validation_without_path_leak(
    tmp_path: Path,
) -> None:
    tools = _build_toolset(tmp_path)
    nextflow_run = tools["nextflow_run"]
    fs_list = tools["fs_list"]

    project = "schema-validation"
    project_root = _project_root(tmp_path, project)
    project_root.mkdir(parents=True)
    (project_root / "samples.csv").write_text("sample,fastq_1\n", encoding="utf-8")

    blocked_list = fs_list(str(tmp_path / "pipelines" / "rnaseq"))
    assert blocked_list["ok"] is False
    assert blocked_list["error"]["error_code"] == "permission_denied"

    parent_listing = fs_list(str(tmp_path), recursive=True, glob="main.nf")
    assert parent_listing["ok"] is True
    assert parent_listing["entries"] == []

    prepared = nextflow_run(
        pipeline="rnaseq",
        project=project,
        params={"input": "samples.csv"},
        validate_params_schema=True,
        prepare=True,
    )

    assert prepared["ok"] is True
    assert prepared["schema_validation"]["errors"] == []
    assert prepared["schema_validation"]["warnings"] == []
    assert "available_defaults" not in prepared["schema_validation"]
    assert "<pipeline_materials_redacted>" in prepared["schema_validation"]["schema_path"]
    assert str((tmp_path / "pipelines").resolve()) not in json.dumps(prepared)


def test_nextflow_run_can_launch_multiple_project_runs_without_process_id_collision(
    tmp_path: Path,
) -> None:
    tools = _build_toolset(tmp_path)
    nextflow_run = tools["nextflow_run"]
    run_get = tools["run_get"]

    first_project = "multi-run-a"
    first_root = _project_root(tmp_path, first_project)
    first_root.mkdir(parents=True)
    (first_root / "samples.csv").write_text("sample,fastq_1\n", encoding="utf-8")

    second_project = "multi-run-b"
    second_root = _project_root(tmp_path, second_project)
    second_root.mkdir(parents=True)
    (second_root / "samples.csv").write_text("sample,fastq_1\n", encoding="utf-8")

    first = nextflow_run(
        pipeline="rnaseq",
        project=first_project,
        params={"input": "samples.csv"},
        detach=False,
    )
    second = nextflow_run(
        pipeline="rnaseq",
        project=second_project,
        params={"input": "samples.csv"},
        detach=False,
    )

    assert first["ok"] is True
    assert second["ok"] is True

    first_full = run_get(str(first["run_id"]), detail="full")
    second_full = run_get(str(second["run_id"]), detail="full")

    assert first_full["process_id"] != second_full["process_id"]
    assert Path(first_full["job_dir"]).name == "job"
    assert Path(second_full["job_dir"]).name == "job"


def test_nextflow_pipeline_discovery_and_inspection(tmp_path: Path) -> None:
    tools = _build_toolset(tmp_path, expose_pipeline_materials=True)
    nextflow_list_pipelines = tools["nextflow_list_pipelines"]
    nextflow_inspect_pipeline = tools["nextflow_inspect_pipeline"]

    listing = nextflow_list_pipelines()
    pipeline_ids = {item["pipeline_id"] for item in listing["pipelines"]}
    assert listing["ok"] is True
    assert pipeline_ids == {"riboseq", "rnaseq"}

    summary = nextflow_inspect_pipeline("rnaseq")
    assert summary["ok"] is True
    assert summary["pipeline_id"] == "rnaseq"
    assert summary["pipeline_dir"] == str((tmp_path / "pipelines" / "rnaseq").resolve())
    assert summary["schema_summary"]["title"] == "RNA-seq test pipeline"

    materials = nextflow_inspect_pipeline("rnaseq", detail="materials")
    assert materials["ok"] is True
    assert materials["schema"]["title"] == "RNA-seq test pipeline"
    assert any(item.get("content") == "# RNA-seq\n" for item in materials["documents"])


def test_nextflow_pipeline_materials_are_disabled_by_default(tmp_path: Path) -> None:
    tools = _build_toolset(tmp_path)
    nextflow_list_pipelines = tools["nextflow_list_pipelines"]
    nextflow_inspect_pipeline = tools["nextflow_inspect_pipeline"]

    listing = nextflow_list_pipelines()
    assert listing["ok"] is True
    assert listing["pipelines"] == [{"pipeline_id": "riboseq"}, {"pipeline_id": "rnaseq"}]

    summary = nextflow_inspect_pipeline("rnaseq")
    assert summary["ok"] is False
    assert summary["error"]["error_code"] == "feature_disabled"
    assert "Pipeline authoring materials are not exposed" in str(summary["error"]["message"])
    assert "server_info().nextflow.pipeline_materials.enabled" in summary["error"]["suggestions"][1]

    materials = nextflow_inspect_pipeline("rnaseq", detail="materials")

    assert materials["ok"] is False
    assert materials["error"]["error_code"] == "feature_disabled"
    assert "Pipeline authoring materials are not exposed" in str(materials["error"]["message"])


def test_pipeline_catalog_stays_available_when_fs_cannot_read_pipeline_root(tmp_path: Path) -> None:
    from fastmcp import FastMCP

    _write_local_pipelines(tmp_path)
    fake_nextflow = _write_fake_nextflow(tmp_path)
    read_root = tmp_path / "read"
    read_root.mkdir()
    samplesheet = read_root / "samples.csv"
    samplesheet.write_text("sample,fastq_1\n", encoding="utf-8")
    write_root = tmp_path / "write"
    db_path = write_root / "state" / "processes.db"

    mcp = FastMCP(name="test")
    cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(read_root)],
            allowed_write_roots=[str(write_root)],
        ),
        state=StateConfig(db_path=str(db_path)),
        nextflow=NextflowConfig(
            executable=str(fake_nextflow),
            pipeline_roots=[str(tmp_path / "pipelines")],
        ),
    )
    runtime = RuntimeState(cfg)
    register_capability_tools(mcp, runtime)
    register_fs_tools(mcp, runtime)
    register_project_tools(mcp, runtime)
    register_run_tools(mcp, runtime)
    register_nextflow_tools(mcp, runtime)
    tools = registered_tool_functions(mcp)

    nextflow_list_pipelines = tools["nextflow_list_pipelines"]
    nextflow_inspect_pipeline = tools["nextflow_inspect_pipeline"]
    nextflow_run = tools["nextflow_run"]
    fs_read = tools["fs_read"]

    listing = nextflow_list_pipelines()
    assert listing["ok"] is True
    assert {item["pipeline_id"] for item in listing["pipelines"]} == {"riboseq", "rnaseq"}

    summary = nextflow_inspect_pipeline("rnaseq")
    assert summary["ok"] is False
    assert summary["error"]["error_code"] == "feature_disabled"

    fs_result = fs_read(str(tmp_path / "pipelines" / "rnaseq" / "README.md"))
    assert fs_result["ok"] is False
    assert fs_result["error"]["error_code"] == "permission_denied"

    run_result = nextflow_run(
        pipeline="rnaseq",
        project="split-roots",
        params={"input": str(samplesheet)},
        detach=False,
    )
    assert run_result["ok"] is True

    explicit_path_result = nextflow_run(
        pipeline=str(tmp_path / "pipelines" / "rnaseq" / "interactive.nf"),
        project="split-roots-explicit",
        params={"input": str(samplesheet)},
        detach=False,
    )
    assert explicit_path_result["ok"] is True


def test_nextflow_tools_return_structured_errors_for_missing_resources(
    tmp_path: Path,
) -> None:
    tools = _build_toolset(tmp_path)
    nextflow_inspect_pipeline = tools["nextflow_inspect_pipeline"]
    run_logs = tools["run_logs"]

    inspect_result = nextflow_inspect_pipeline("missing-pipeline")
    assert inspect_result["ok"] is False
    assert inspect_result["error"]["error_code"] == "feature_disabled"

    run_error = assert_tool_error(run_logs("missing-run"), "not_found")
    assert "Unknown run" in str(run_error["message"])


def _build_toolset(
    tmp_path: Path,
    *,
    default_profile: str | None = "docker",
    igenomes_ignore: bool = False,
    fake_mode: str = "success",
    allowed_read_roots: list[str] | None = None,
    expose_pipeline_materials: bool = False,
) -> dict[str, Any]:
    """Register project/run/nextflow tools with a fake executable."""
    from fastmcp import FastMCP

    _write_local_pipelines(tmp_path)
    db_path = tmp_path / "state" / "processes.db"
    fake_nextflow = _write_fake_nextflow(tmp_path, mode=fake_mode)

    mcp = FastMCP(name="test")
    cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=(
                allowed_read_roots if allowed_read_roots is not None else [str(tmp_path)]
            ),
            allowed_write_roots=[str(tmp_path)],
        ),
        state=StateConfig(db_path=str(db_path)),
        nextflow=NextflowConfig(
            executable=str(fake_nextflow),
            pipeline_roots=[str(tmp_path / "pipelines")],
            default_profile=default_profile,
            igenomes_ignore=igenomes_ignore,
            expose_pipeline_materials=expose_pipeline_materials,
            env={
                "NXF_HOME": "/tmp/fake-nxf-home",
                "NF_SHARED": "from-config",
            },
        ),
    )
    runtime = RuntimeState(cfg)
    register_capability_tools(mcp, runtime)
    register_fs_tools(mcp, runtime)
    register_project_tools(mcp, runtime)
    register_run_tools(mcp, runtime)
    register_nextflow_tools(mcp, runtime)
    return registered_tool_functions(mcp)


def _project_root(tmp_path: Path, project: str) -> Path:
    """Return the default project root for one project identifier."""
    return tmp_path / "projects" / project


def _write_local_pipelines(tmp_path: Path) -> None:
    """Create a small local pipeline catalog for testing."""
    pipelines_root = tmp_path / "pipelines"

    rnaseq_dir = pipelines_root / "rnaseq"
    (rnaseq_dir / "docs").mkdir(parents=True)
    (rnaseq_dir / "workflows").mkdir(parents=True)
    (rnaseq_dir / "main.nf").write_text("workflow {}\n", encoding="utf-8")
    (rnaseq_dir / "interactive.nf").write_text("workflow interactive {}\n", encoding="utf-8")
    (rnaseq_dir / "nextflow.config").write_text("manifest.name = 'rnaseq'\n", encoding="utf-8")
    (rnaseq_dir / "README.md").write_text("# RNA-seq\n", encoding="utf-8")
    (rnaseq_dir / "docs" / "usage.md").write_text("Run with --input\n", encoding="utf-8")
    (rnaseq_dir / "workflows" / "main.nf").write_text("workflow main {}\n", encoding="utf-8")
    (rnaseq_dir / "nextflow_schema.json").write_text(
        json.dumps(
            {
                "title": "RNA-seq test pipeline",
                "description": "Test schema for local rnaseq pipeline discovery.",
                "type": "object",
                "$defs": {
                    "input_output_options": {
                        "type": "object",
                        "required": ["input", "outdir"],
                        "properties": {
                            "input": {"type": "string"},
                            "outdir": {"type": "string"},
                            "threads": {"type": "integer", "default": 8},
                            "enabled": {"type": "boolean", "default": False},
                            "help": {"type": ["boolean", "string"], "default": False},
                        },
                    }
                },
                "allOf": [{"$ref": "#/$defs/input_output_options"}],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    riboseq_dir = pipelines_root / "riboseq"
    riboseq_dir.mkdir(parents=True)
    (riboseq_dir / "main.nf").write_text("workflow {}\n", encoding="utf-8")
    (riboseq_dir / "README.md").write_text("# Ribo-seq\n", encoding="utf-8")


def _write_fake_nextflow(tmp_path: Path, *, mode: str = "success") -> Path:
    """Create a fake Nextflow executable that records argv and env."""
    script = tmp_path / "fake_nextflow.py"
    script.write_text(
        "\n".join(
            [
                f"#!{sys.executable}",
                "import json",
                "import os",
                "import sys",
                "from pathlib import Path",
                "",
                f"mode = {mode!r}",
                f"session_uuid = {SESSION_UUID!r}",
                "args = sys.argv[1:]",
                "log_path = args[args.index('-log') + 1]",
                "work_dir = None",
                "if '-work-dir' in args:",
                "    work_dir = Path(args[args.index('-work-dir') + 1])",
                "    work_dir.mkdir(parents=True, exist_ok=True)",
                "if mode == 'task_failure':",
                "    task_dir = work_dir / 'ab' / 'cdef'",
                "    task_dir.mkdir(parents=True, exist_ok=True)",
                "    (task_dir / '.command.err').write_text(",
                "        '/bin/bash: salmon: command not found\\n',",
                "        encoding='utf-8',",
                "    )",
                "    nextflow_lines = [",
                "        f'Session UUID: {session_uuid}',",
                "        'executor >  local (1)',",
                "        \"ERROR ~ Error executing process > 'ALIGN_READS (sample1)'\",",
                "        '',",
                "        'Caused by:',",
                (
                    "        '  Process `ALIGN_READS (sample1)` terminated with an "
                    "error exit status (127)',"
                ),
                "        '',",
                "        'Work dir:',",
                "        f'  {task_dir}',",
                "    ]",
                (
                    "    Path(log_path).write_text('\\n'.join(nextflow_lines) + '\\n', "
                    "encoding='utf-8')"
                ),
                "    sys.exit(1)",
                (
                    "Path(log_path).write_text("
                    "f'Session UUID: {session_uuid}\\nfake nextflow log\\n', "
                    "encoding='utf-8'"
                    ")"
                ),
                "for index, arg in enumerate(args):",
                "    if arg == '--outdir' and index + 1 < len(args):",
                "        outdir = Path(args[index + 1])",
                "        outdir.mkdir(parents=True, exist_ok=True)",
                "        (outdir / 'summary.txt').write_text('done\\n', encoding='utf-8')",
                "    if arg == '-with-report' and index + 1 < len(args):",
                "        Path(args[index + 1]).write_text('fake report\\n', encoding='utf-8')",
                "print(json.dumps({",
                "    'argv': args,",
                "    'env': {",
                "        'NXF_HOME': os.environ.get('NXF_HOME'),",
                "        'NF_SHARED': os.environ.get('NF_SHARED'),",
                "        'NF_ONLY': os.environ.get('NF_ONLY'),",
                "    },",
                "}))",
            ]
        ),
        encoding="utf-8",
    )
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return script


def assert_subsequence(haystack: list[str], needle: list[str]) -> None:
    """Assert that one list appears contiguously inside another."""
    width = len(needle)
    for index in range(len(haystack) - width + 1):
        if haystack[index : index + width] == needle:
            return
    raise AssertionError(f"Subsequence not found: {needle} in {haystack}")
