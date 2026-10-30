"""Tests for nextmcp.tools.fs_tools."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from nextmcp.config import AppConfig, AuthConfig, PathsConfig, ServerConfig, StateConfig
from nextmcp.runtime_state import RuntimeState
from nextmcp.tools.fs_tools import _entry_info, register_fs_tools
from tests.conftest import assert_tool_error, registered_tool_functions


@pytest.fixture
def fs_tools(data_dir: Path) -> dict[str, Any]:
    """Register fs tools on a throwaway FastMCP and return the raw callables."""
    from fastmcp import FastMCP

    mcp = FastMCP(name="test")
    service_root = data_dir.parent / "service-state"
    cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(data_dir.parent)],
            allowed_write_roots=[str(data_dir.parent)],
        ),
        state=StateConfig(db_path=str(service_root / "state" / "processes.db")),
    )
    register_fs_tools(mcp, RuntimeState(cfg))

    return registered_tool_functions(mcp)


# ── fs_list ──────────────────────────────────────────────


def test_fs_list_basic(fs_tools, data_dir: Path) -> None:
    fs_list = fs_tools["fs_list"]
    result = fs_list(path=str(data_dir))
    assert result["ok"] is True
    names = {e["name"] for e in result["entries"]}
    assert "file_a.txt" in names
    assert "file_b.fastq.gz" in names
    assert "subdir" in names
    assert result["count"] == 3


def test_fs_list_recursive(fs_tools, data_dir: Path) -> None:
    fs_list = fs_tools["fs_list"]
    result = fs_list(path=str(data_dir), recursive=True)
    names = {e["name"] for e in result["entries"]}
    assert "nested.txt" in names
    assert result["count"] >= 4  # subdir, file_a, file_b, nested


def test_fs_list_glob(fs_tools, data_dir: Path) -> None:
    fs_list = fs_tools["fs_list"]
    result = fs_list(path=str(data_dir), glob="*.txt")
    names = {e["name"] for e in result["entries"]}
    assert names == {"file_a.txt"}


def test_fs_list_glob_mode_requires_pattern(fs_tools, data_dir: Path) -> None:
    fs_list = fs_tools["fs_list"]
    error = assert_tool_error(
        fs_list(path=str(data_dir), mode="glob"),
        "invalid_arguments",
    )
    assert "requires a glob pattern" in str(error["message"])


def test_fs_list_manifest_for_file(fs_tools, data_dir: Path) -> None:
    fs_list = fs_tools["fs_list"]
    result = fs_list(path=str(data_dir / "file_a.txt"), mode="manifest")
    assert result["ok"] is True
    assert "entries" not in result
    assert "count" not in result
    assert result["target"]["type"] == "file"
    assert result["summary"] == {
        "target_type": "file",
        "files": 1,
        "dirs": 0,
        "total_size": len("line1\nline2\nline3\n"),
    }


def test_fs_list_manifest_can_limit_fields(fs_tools, data_dir: Path) -> None:
    fs_list = fs_tools["fs_list"]
    result = fs_list(
        path=str(data_dir),
        mode="manifest",
        fields=["name", "type"],
    )
    assert result["ok"] is True
    assert result["fields"] == ["name", "type"]
    assert set(result["target"]) == {"name", "type"}
    assert "summary" in result


def test_fs_list_limit(fs_tools, data_dir: Path) -> None:
    fs_list = fs_tools["fs_list"]
    result = fs_list(path=str(data_dir), limit=1)
    assert result["count"] == 1


def test_fs_list_not_a_dir(fs_tools, data_dir: Path) -> None:
    fs_list = fs_tools["fs_list"]
    error = assert_tool_error(
        fs_list(path=str(data_dir / "file_a.txt")),
        "not_found",
    )
    assert "Not a directory" in str(error["message"])


def test_fs_list_denied(fs_tools) -> None:
    fs_list = fs_tools["fs_list"]
    assert_tool_error(fs_list(path="/etc"), "permission_denied")


# ── fs_read ──────────────────────────────────────────────


def test_fs_read_full(fs_tools, data_dir: Path) -> None:
    fs_read = fs_tools["fs_read"]
    result = fs_read(path=str(data_dir / "file_a.txt"))
    assert result["ok"] is True
    assert result["truncated"] is False
    assert result["content"] == "line1\nline2\nline3\n"
    assert result["total_lines"] == 3


def test_fs_read_line_range(fs_tools, data_dir: Path) -> None:
    fs_read = fs_tools["fs_read"]
    result = fs_read(path=str(data_dir / "file_a.txt"), start_line=2, end_line=2)
    assert result["content"] == "line2\n"


def test_fs_read_tail(fs_tools, data_dir: Path) -> None:
    fs_read = fs_tools["fs_read"]
    result = fs_read(path=str(data_dir / "file_a.txt"), tail=1)
    assert result["content"] == "line3\n"


def test_fs_read_truncation(fs_tools, data_dir: Path) -> None:
    fs_read = fs_tools["fs_read"]
    result = fs_read(path=str(data_dir / "file_a.txt"), max_bytes=5)
    assert result["truncated"] is True
    assert len(result["content"]) <= 5


def test_fs_read_not_a_file(fs_tools, data_dir: Path) -> None:
    fs_read = fs_tools["fs_read"]
    error = assert_tool_error(
        fs_read(path=str(data_dir / "subdir")),
        "not_found",
    )
    assert "Not a file" in str(error["message"])


def test_fs_write_overwrite(fs_tools, data_dir: Path) -> None:
    fs_write = fs_tools["fs_write"]
    result = fs_write(path=str(data_dir / "file_a.txt"), content="rewritten\n")
    assert result["created"] is False
    assert result["appended"] is False
    assert (data_dir / "file_a.txt").read_text() == "rewritten\n"


def test_fs_write_append(fs_tools, data_dir: Path) -> None:
    fs_write = fs_tools["fs_write"]
    result = fs_write(path=str(data_dir / "file_a.txt"), content="tail\n", append=True)
    assert result["appended"] is True
    assert (data_dir / "file_a.txt").read_text().endswith("tail\n")


def test_fs_write_create_parents(fs_tools, data_dir: Path) -> None:
    fs_write = fs_tools["fs_write"]
    result = fs_write(
        path=str(data_dir / "new" / "nested" / "created.txt"),
        content="hello\n",
        create_parents=True,
    )
    assert result["created"] is True
    assert (data_dir / "new" / "nested" / "created.txt").read_text() == "hello\n"


def test_fs_write_denied(fs_tools) -> None:
    fs_write = fs_tools["fs_write"]
    assert_tool_error(
        fs_write(path="/etc/forbidden.txt", content="x"),
        "permission_denied",
    )


def test_fs_write_rejects_symlink(fs_tools, data_dir: Path, tmp_path: Path) -> None:
    fs_write = fs_tools["fs_write"]
    outside = tmp_path.parent / "outside-write.txt"
    outside.write_text("outside\n")
    link = data_dir / "write-link.txt"
    link.symlink_to(outside)

    error = assert_tool_error(
        fs_write(path=str(link), content="blocked\n"),
        "invalid_arguments",
    )
    assert "symlink" in str(error["message"])


def test_fs_mkdir_creates_directory(fs_tools, data_dir: Path) -> None:
    fs_mkdir = fs_tools["fs_mkdir"]
    result = fs_mkdir(path=str(data_dir / "mkdir" / "child"))
    assert result["created"] is True
    assert (data_dir / "mkdir" / "child").is_dir()


def test_fs_tools_do_not_expose_fs_delete(fs_tools) -> None:
    assert "fs_delete" not in fs_tools


def test_fs_copy_file(fs_tools, data_dir: Path) -> None:
    fs_copy = fs_tools["fs_copy"]
    target = data_dir / "copies" / "file_a.txt"
    result = fs_copy(
        src=str(data_dir / "file_a.txt"),
        dst=str(target),
        create_parents=True,
    )
    assert result["copied"] is True
    assert target.read_text() == "line1\nline2\nline3\n"


def test_fs_copy_directory_requires_recursive(fs_tools, data_dir: Path) -> None:
    fs_copy = fs_tools["fs_copy"]
    error = assert_tool_error(
        fs_copy(src=str(data_dir / "subdir"), dst=str(data_dir / "subdir-copy")),
        "invalid_path_type",
    )
    assert "recursive=True" in str(error["message"])


def test_fs_copy_directory_recursive(fs_tools, data_dir: Path) -> None:
    fs_copy = fs_tools["fs_copy"]
    target = data_dir / "subdir-copy"
    result = fs_copy(
        src=str(data_dir / "subdir"),
        dst=str(target),
        recursive=True,
    )
    assert result["type"] == "dir"
    assert (target / "nested.txt").read_text() == "nested content\n"


def test_fs_move_file(fs_tools, data_dir: Path) -> None:
    fs_move = fs_tools["fs_move"]
    source = data_dir / "file_a.txt"
    destination = data_dir / "moved" / "file_a.txt"
    result = fs_move(
        src=str(source),
        dst=str(destination),
        create_parents=True,
    )
    assert result["moved"] is True
    assert not source.exists()
    assert destination.read_text() == "line1\nline2\nline3\n"


def test_fs_move_requires_write_access_for_source(fs_tools, tmp_path: Path) -> None:
    fs_move = fs_tools["fs_move"]
    outside = tmp_path.parent / "outside-move.txt"
    outside.write_text("x")
    assert_tool_error(
        fs_move(src=str(outside), dst=str(tmp_path / "inside.txt")),
        "permission_denied",
    )


# ── _entry_info ──────────────────────────────────────────


def test_entry_info_file_and_dir(data_dir: Path) -> None:
    file_info = _entry_info(data_dir / "file_a.txt")
    assert file_info["type"] == "file"
    assert file_info["name"] == "file_a.txt"
    assert isinstance(file_info["size"], int) and file_info["size"] > 0
    assert isinstance(file_info["mtime"], str)

    dir_info = _entry_info(data_dir / "subdir")
    assert dir_info["type"] == "dir"
    assert dir_info["size"] is None
