"""Shared fixtures for nextmcp tests."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest

from nextmcp.config import AppConfig, AuthConfig, PathsConfig, ServerConfig
from nextmcp.paths import PathGuard


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """Create a temporary directory tree for filesystem tests."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "file_a.txt").write_text("line1\nline2\nline3\n")
    (workspace / "file_b.fastq.gz").write_bytes(b"\x1f\x8b fake gz")
    sub = workspace / "subdir"
    sub.mkdir()
    (sub / "nested.txt").write_text("nested content\n")
    return workspace


@pytest.fixture
def app_config(tmp_path: Path) -> AppConfig:
    """AppConfig with allowed roots = tmp_path, auth disabled."""
    return AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(tmp_path)],
            allowed_write_roots=[str(tmp_path)],
        ),
    )


@pytest.fixture
def guard(app_config: AppConfig) -> PathGuard:
    """PathGuard backed by app_config."""
    return PathGuard(app_config.paths)


def assert_tool_error(result: dict[str, object], error_code: str) -> dict[str, object]:
    """Assert that a tool returned a structured error payload."""
    assert result["ok"] is False
    error = result["error"]
    assert isinstance(error, dict)
    assert error["error_code"] == error_code
    return error


def registered_tool_functions(mcp: Any) -> dict[str, Any]:
    """Expose registered tool callables across the supported FastMCP versions."""
    return {tool.name: tool.fn for tool in _registered_tool_defs(mcp)}


def registered_tools(mcp: Any) -> dict[str, Any]:
    """Expose registered tool definitions across the supported FastMCP versions."""
    return {tool.name: tool for tool in _registered_tool_defs(mcp)}


def _registered_tool_defs(mcp: Any) -> list[Any]:
    """Collect registered tool definitions from the current FastMCP instance."""
    if hasattr(mcp, "list_tools"):
        return list(asyncio.run(mcp.list_tools()))

    tool_manager = getattr(mcp, "_tool_manager", None)
    if tool_manager is None:
        raise AttributeError("FastMCP instance does not expose a supported tool registry API")
    return list(tool_manager._tools.values())
