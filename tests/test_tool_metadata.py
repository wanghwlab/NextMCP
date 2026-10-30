"""Tests for MCP-visible tool descriptions and parameter metadata."""

from __future__ import annotations

from pathlib import Path

from nextmcp.config import AppConfig, AuthConfig, PathsConfig, ServerConfig, StateConfig
from nextmcp.runtime_state import RuntimeState
from nextmcp.tools.capability_tools import register_capability_tools
from nextmcp.tools.fs_tools import register_fs_tools
from nextmcp.tools.nextflow_tools import register_nextflow_tools
from nextmcp.tools.project_tools import register_project_tools
from nextmcp.tools.run_tools import register_run_tools
from tests.conftest import registered_tools


def _collapse_whitespace(value: str) -> str:
    return " ".join(value.split())


def test_fs_tools_expose_usage_guidance_and_parameter_descriptions(tmp_path: Path) -> None:
    from fastmcp import FastMCP

    mcp = FastMCP(name="test")
    cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(tmp_path)],
            allowed_write_roots=[str(tmp_path)],
        ),
        state=StateConfig(db_path=str(tmp_path / "state" / "processes.db")),
    )
    register_fs_tools(mcp, RuntimeState(cfg))

    tools = registered_tools(mcp)
    fs_list = tools["fs_list"]
    fs_read = tools["fs_read"]
    fs_write = tools["fs_write"]
    fs_list_description = _collapse_whitespace(fs_list.description)
    fs_read_description = _collapse_whitespace(fs_read.description)

    assert "fs_delete" not in tools
    assert "first filesystem tool" in fs_list_description
    assert "not on the client machine" in fs_list_description
    assert "configured pipeline repository paths is rejected" in fs_list_description
    assert 'Use `mode="manifest"` when you need a stat-like summary' in fs_list.description
    assert "configured pipeline repository files cannot be read" in fs_read_description
    assert fs_list.parameters["properties"]["path"]["description"].startswith(
        "Path to inspect on the nextmcp server filesystem."
    )
    assert fs_list.parameters["properties"]["mode"]["description"].startswith("Listing mode.")
    assert "Prefer `fs_list` or `fs_read` first" in fs_write.description
    assert fs_write.parameters["properties"]["content"]["description"] == (
        "UTF-8 text content to write or append."
    )


def test_project_and_run_tools_expose_project_mode_guidance(tmp_path: Path) -> None:
    from fastmcp import FastMCP

    mcp = FastMCP(name="test")
    cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(tmp_path)],
            allowed_write_roots=[str(tmp_path)],
        ),
        state=StateConfig(db_path=str(tmp_path / "state" / "processes.db")),
    )
    runtime = RuntimeState(cfg)
    register_project_tools(mcp, runtime)
    register_run_tools(mcp, runtime)

    tools = registered_tools(mcp)
    project_list = tools["project_list"]
    project_get = tools["project_get"]
    run_list = tools["run_list"]
    run_get = tools["run_get"]
    run_artifacts = tools["run_artifacts"]
    run_logs = tools["run_logs"]
    run_stop = tools["run_stop"]
    project_list_description = _collapse_whitespace(project_list.description)
    project_get_description = _collapse_whitespace(project_get.description)
    run_list_description = _collapse_whitespace(run_list.description)
    run_get_description = _collapse_whitespace(run_get.description)
    run_artifacts_description = _collapse_whitespace(run_artifacts.description)
    run_logs_description = _collapse_whitespace(run_logs.description)

    assert "process_list" not in tools
    assert "process_get" not in tools
    assert "process_logs" not in tools
    assert "process_artifacts" not in tools
    assert "process_stop" not in tools
    assert "process_delete" not in tools
    assert "run_resume" not in tools
    assert "known projects" in project_list_description
    assert "project" in project_get_description
    assert "rediscover a `run_id`" in run_list_description
    assert run_list.parameters["properties"]["project"]["description"].startswith(
        "Optional exact project filter."
    )
    assert run_list.parameters["properties"]["pipeline"]["description"].startswith(
        "Optional exact Nextflow pipeline filter."
    )
    assert run_list.parameters["properties"]["artifact_path_contains"]["description"].startswith(
        "Optional substring match against indexed artifact paths"
    )
    assert run_list.parameters["properties"]["finished_after"]["description"].startswith(
        "Optional inclusive lower bound for `finished_at`"
    )
    assert run_list.parameters["properties"]["detail"]["description"].startswith(
        "Response detail level."
    )
    assert "workflow run" in run_get_description
    assert "`run_layout`" in run_get.description
    assert "`launch_spec`" in run_get.description
    assert "`nextflow_session_uuid`" in run_get.description
    assert "pipeline repository paths are redacted" in run_list_description
    assert "pipeline repository paths are redacted" in run_get_description
    assert run_get.parameters["properties"]["run_id"]["description"].startswith(
        "Run identifier returned by `nextflow_run` or listed by `run_list`."
    )
    assert run_get.parameters["properties"]["detail"]["description"].startswith(
        "Response detail level."
    )
    assert set(run_logs.parameters["properties"]["stream"]["enum"]) == {
        "stdout",
        "stderr",
        "nextflow",
    }
    assert set(run_artifacts.parameters["properties"]["section"]["enum"]) == {
        "record_files",
        "declared_outputs",
        "published_roots",
        "items",
    }
    assert run_logs.parameters["properties"]["after_line"]["description"].startswith(
        "Return only lines strictly after this 1-based line number"
    )
    assert run_logs.parameters["properties"]["stream"]["description"].startswith(
        "Which log stream to inspect."
    )
    assert run_logs.parameters["properties"]["view"]["description"].startswith("Response mode.")
    assert run_logs.parameters["properties"]["run_id"]["description"].startswith(
        "Run identifier returned by `nextflow_run` or listed by `run_list`."
    )
    assert "server-side project root" in run_get.description
    assert run_get.parameters["properties"]["include"]["description"].startswith(
        "Optional extra sections. Leave this empty for routine status polling"
    )
    assert run_artifacts.parameters["properties"]["detail"]["description"].startswith(
        "Response detail level."
    )
    assert run_artifacts.parameters["properties"]["limit"]["description"].startswith(
        "Maximum number of artifact entries to return."
    )
    assert run_artifacts.parameters["properties"]["root_label"]["description"].startswith(
        "Optional published-root label filter."
    )
    assert "Use `run_get(run_id)` first" in run_logs.description
    assert '`view="important"` returns a compact' in run_logs_description
    assert "`after_line` supports incremental fetches" in run_logs_description
    assert "redacted even from raw log content" in run_logs_description
    assert "one section at a time" in run_artifacts_description
    assert (
        "run-owned logs and JSON"
        in run_artifacts.parameters["properties"]["section"]["description"]
    )
    assert "underlying process group" in run_stop.parameters["properties"]["force"]["description"]


def test_nextflow_tools_expose_discovery_first_guidance(tmp_path: Path) -> None:
    from fastmcp import FastMCP

    mcp = FastMCP(name="test")
    cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(tmp_path)],
            allowed_write_roots=[str(tmp_path)],
        ),
        state=StateConfig(db_path=str(tmp_path / "state" / "processes.db")),
    )
    runtime = RuntimeState(cfg)
    register_project_tools(mcp, runtime)
    register_run_tools(mcp, runtime)
    register_nextflow_tools(mcp, runtime)

    tools = registered_tools(mcp)
    get_tool = tools["nextflow_inspect_pipeline"]
    run_tool = tools["nextflow_run"]
    get_tool_description = _collapse_whitespace(get_tool.description)
    run_tool_description = _collapse_whitespace(run_tool.description)

    assert "authoring and package-maintenance tool" in get_tool_description
    assert "do not call this tool for ordinary runtime planning" in get_tool_description
    assert "server_info().nextflow.pipeline_materials.enabled" in get_tool.description
    assert "For a new run, provide `project` and `pipeline`" in run_tool_description
    assert "All paths refer to the nextmcp server filesystem." in run_tool_description
    assert "prepare=true" in run_tool_description
    assert "validate_params_schema=true" in run_tool_description
    assert "expected artifact paths" in run_tool_description
    assert "pipeline repository paths and schema file paths" in run_tool_description
    assert "Returns a compact run summary." in run_tool_description
    assert run_tool.parameters["properties"]["pipeline"]["description"].startswith(
        "Configured pipeline ID or remote pipeline identifier."
    )
    assert "from_run_id" in run_tool.parameters["properties"]
    assert run_tool.parameters["properties"]["from_run_id"]["description"].startswith(
        "Optional source run identifier."
    )
    assert run_tool.parameters["properties"]["project"]["description"].startswith(
        "Project identifier used to place this run under the configured projects root."
    )
    assert (
        "Required unless `from_run_id` is provided."
        in run_tool.parameters["properties"]["project"]["description"]
    )
    assert get_tool.parameters["properties"]["detail"]["description"].startswith(
        "Call only when `server_info().nextflow.pipeline_materials.enabled`"
    )
    assert run_tool.parameters["properties"]["run_id"]["description"].startswith(
        "Optional explicit run identifier."
    )
    assert "from_run_id" in run_tool_description
    assert run_tool.parameters["properties"]["run_name"]["description"].startswith(
        "Optional human-readable name stored with the run record."
    )
    config_files_schema = run_tool.parameters["properties"]["config_files"]
    assert config_files_schema["description"].startswith(
        "Optional Nextflow config file path or list of config files on the server."
    )
    assert "anyOf" in config_files_schema
    assert any(item.get("type") == "string" for item in config_files_schema["anyOf"])
    assert any(item.get("type") == "array" for item in config_files_schema["anyOf"])
    assert "cwd" not in run_tool.parameters["properties"]
    assert "work_dir" not in run_tool.parameters["properties"]
    assert "label" not in run_tool.parameters["properties"]
    assert "resume" not in run_tool.parameters["properties"]
    assert "resume_session_id" not in run_tool.parameters["properties"]
    assert "reuse_run_id" not in run_tool.parameters["properties"]
    assert run_tool.parameters["properties"]["prepare"]["description"].startswith(
        "If true, resolve the final Nextflow launch plan"
    )
    assert run_tool.parameters["properties"]["validate_params_schema"]["description"].startswith(
        "If true, validate CLI `params` against a local `nextflow_schema.json`"
    )
    assert (
        "Public responses redact schema file paths"
        in run_tool.parameters["properties"]["validate_params_schema"]["description"]
    )


def test_server_info_exposes_environment_discovery_guidance(tmp_path: Path) -> None:
    from fastmcp import FastMCP

    mcp = FastMCP(name="test")
    cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(tmp_path)],
            allowed_write_roots=[str(tmp_path)],
        ),
        state=StateConfig(db_path=str(tmp_path / "state" / "processes.db")),
    )
    register_capability_tools(mcp, RuntimeState(cfg))

    tools = registered_tools(mcp)
    server_info = tools["server_info"]
    server_info_description = _collapse_whitespace(server_info.description)

    assert "without reading `config.yaml` directly" in server_info_description
    assert "not the client machine" in server_info_description
    assert "Use `nextflow_list_pipelines` after this only when" in server_info_description
    assert "concrete local pipeline ID is still unknown" in server_info_description
    assert "`nextflow.pipeline_materials.enabled` is false" in server_info_description
    assert "pipeline repository paths are not returned" in server_info_description
    assert "`nextflow.pipeline_materials` policy" in server_info.description
    assert "`readiness`" in server_info.description
    assert "This tool also returns a compact readiness check" in server_info_description
    assert server_info.parameters["properties"] == {}
    assert "nextflow.env" in server_info_description
