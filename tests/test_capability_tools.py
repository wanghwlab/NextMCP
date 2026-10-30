"""Tests for nextmcp.tools.capability_tools."""

from __future__ import annotations

import sys
from pathlib import Path

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
from tests.conftest import registered_tool_functions


def test_server_info_returns_safe_runtime_summary(tmp_path: Path) -> None:
    from fastmcp import FastMCP

    read_root = tmp_path / "read"
    write_root = tmp_path / "write"
    pipelines_root = tmp_path / "pipelines"
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
            executable="nextflow",
            pipeline_roots=[str(pipelines_root)],
            expose_pipeline_materials=True,
            env={"ACCESS_KEY": "secret-value", "NXF_HOME": "/tmp/nxf"},
        ),
    )
    runtime = RuntimeState(cfg)
    register_capability_tools(mcp, runtime)

    server_info = registered_tool_functions(mcp)["server_info"]
    result = server_info()

    assert result["ok"] is True
    assert result["paths"] == {
        "allowed_read_roots": [str(read_root.resolve())],
        "allowed_write_roots": [str(write_root.resolve())],
    }
    assert result["projects"] == {
        "root": str((write_root / "projects").resolve()),
    }
    assert result["nextflow"] == {
        "default_profile": "docker",
        "local_pipeline_catalog": {
            "enabled": True,
            "configured_root_count": 1,
        },
        "pipeline_materials": {
            "enabled": True,
            "intended_use": "authoring_only",
            "ordinary_runtime_should_call": False,
        },
    }
    assert set(result["readiness"]) == {"ok", "checks", "blocking_issues", "warnings"}
    assert "configured" not in result["readiness"]["checks"]["nextflow_executable"]
    assert "path" not in result["readiness"]["checks"]["projects_root"]
    assert result["readiness"]["checks"]["local_pipeline_catalog"] == {
        "enabled": True,
        "configured_root_count": 1,
        "readable_root_count": 0,
        "missing_root_count": 1,
        "unreadable_root_count": 0,
        "pipeline_count": 0,
    }
    assert result["readiness"]["warnings"] == ["1 configured pipeline roots do not exist."]
    assert "env" not in result["nextflow"]


def test_server_info_reads_the_current_runtime_snapshot(tmp_path: Path) -> None:
    from fastmcp import FastMCP

    first_read_root = tmp_path / "read-a"
    first_write_root = tmp_path / "write-a"
    second_read_root = tmp_path / "read-b"
    second_write_root = tmp_path / "write-b"

    mcp = FastMCP(name="test")
    initial_cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(first_read_root)],
            allowed_write_roots=[str(first_write_root)],
        ),
        state=StateConfig(db_path=str(first_write_root / "state" / "processes.db")),
        nextflow=NextflowConfig(
            executable="nextflow",
            pipeline_roots=[],
        ),
    )
    runtime = RuntimeState(initial_cfg)
    register_capability_tools(mcp, runtime)
    server_info = registered_tool_functions(mcp)["server_info"]

    updated_cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(second_read_root)],
            allowed_write_roots=[str(second_write_root)],
        ),
        state=StateConfig(db_path=str(second_write_root / "state" / "processes.db")),
        nextflow=NextflowConfig(
            executable="/usr/local/bin/nextflow",
            pipeline_roots=[str(second_read_root / "pipelines")],
        ),
    )
    runtime.reload(updated_cfg)

    result = server_info()

    assert result["ok"] is True
    assert result["paths"]["allowed_read_roots"] == [str(second_read_root.resolve())]
    assert result["paths"]["allowed_write_roots"] == [str(second_write_root.resolve())]
    assert result["projects"]["root"] == str((second_write_root / "projects").resolve())
    assert result["nextflow"] == {
        "default_profile": "docker",
        "local_pipeline_catalog": {
            "enabled": True,
            "configured_root_count": 1,
        },
        "pipeline_materials": {
            "enabled": False,
            "intended_use": "authoring_only",
            "ordinary_runtime_should_call": False,
        },
    }
    assert "readiness" in result


def test_server_info_always_returns_readiness_summary(tmp_path: Path) -> None:
    from fastmcp import FastMCP

    read_root = tmp_path / "read"
    write_root = tmp_path / "write"
    pipelines_root = read_root / "pipelines"
    pipelines_root.mkdir(parents=True)
    (pipelines_root / "rnaseq").mkdir()
    (pipelines_root / "rnaseq" / "main.nf").write_text("workflow {}\n", encoding="utf-8")

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
            executable=sys.executable,
            pipeline_roots=[str(pipelines_root)],
        ),
    )
    runtime = RuntimeState(cfg)
    register_capability_tools(mcp, runtime)

    server_info = registered_tool_functions(mcp)["server_info"]
    result = server_info()

    assert result["ok"] is True
    assert result["readiness"]["ok"] is True
    assert result["readiness"]["checks"]["nextflow_executable"]["available"] is True
    assert "configured" not in result["readiness"]["checks"]["nextflow_executable"]
    assert "path" not in result["readiness"]["checks"]["projects_root"]
    assert result["readiness"]["checks"]["local_pipeline_catalog"] == {
        "enabled": True,
        "configured_root_count": 1,
        "readable_root_count": 1,
        "missing_root_count": 0,
        "unreadable_root_count": 0,
        "pipeline_count": 1,
    }
    assert result["readiness"]["blocking_issues"] == []
