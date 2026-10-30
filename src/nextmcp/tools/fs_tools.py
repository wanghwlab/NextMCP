"""Filesystem tools: read, write, and directory operations."""

from __future__ import annotations

import fnmatch
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Any, Literal, cast

from fastmcp import FastMCP

from nextmcp.pipeline_visibility import (
    assert_not_pipeline_material_path,
    redact_pipeline_materials,
    resolve_pipeline_roots,
)
from nextmcp.runtime_state import RuntimeState
from nextmcp.tool_response import structured_tool

SERVER_CWD_DESCRIPTION = (
    "Server-side working directory used to resolve relative paths. "
    "Pass this explicitly when needed."
)
FS_ENTRY_FIELDS: tuple[
    Literal["name"],
    Literal["path"],
    Literal["type"],
    Literal["size"],
    Literal["mtime"],
] = ("name", "path", "type", "size", "mtime")


def register_fs_tools(mcp: FastMCP, runtime: RuntimeState) -> None:
    """Register filesystem tools on the MCP server."""

    @mcp.tool
    @structured_tool
    def fs_list(
        path: Annotated[
            str,
            (
                "Path to inspect on the nextmcp server filesystem. "
                "Use an absolute server path or make it relative to `cwd`."
            ),
        ] = ".",
        cwd: Annotated[
            str | None,
            SERVER_CWD_DESCRIPTION,
        ] = None,
        mode: Annotated[
            Literal["list", "glob", "manifest"],
            (
                "Listing mode. Use `list` for normal directory entries, `glob` "
                "for explicit pattern scans, or `manifest` for a compact target "
                "summary that also works for single files."
            ),
        ] = "list",
        recursive: Annotated[bool, "If true, include nested files and directories."] = False,
        glob: Annotated[
            str | None,
            "Optional fnmatch pattern applied to entry names, for example `*.fastq.gz`.",
        ] = None,
        fields: Annotated[
            list[Literal["name", "path", "type", "size", "mtime"]] | None,
            (
                "Optional subset of entry fields to return. Defaults to "
                "`name`, `path`, `type`, `size`, and `mtime`."
            ),
        ] = None,
        limit: Annotated[int, "Maximum number of matching entries to return."] = 500,
    ) -> dict[str, Any]:
        """Inspect one server-side path under the read allowlist.

        All paths are resolved on the nextmcp server, not on the client
        machine. If `server_info().nextflow.pipeline_materials.enabled` is
        false, direct access to configured pipeline repository paths is
        rejected and recursive listings omit hidden pipeline material entries.

        Use this as the first filesystem tool when you need to confirm a path,
        inspect entries before `fs_read`, or verify a target before a mutating
        `fs_*` call. Use `mode="manifest"` when you need a stat-like summary
        without introducing a separate filesystem tool.

        Returns `ok: true` with the resolved server `path`, a `count`, and an
        `entries` array. `manifest` mode also returns a compact `target`
        summary plus aggregate counts so agents can confirm one path with less
        context. For file targets, manifest mode omits the redundant
        single-item `entries` array.
        """
        snapshot = runtime.snapshot()
        guard = snapshot.guard
        resolved = guard.resolve_read(path, cwd)
        _reject_hidden_pipeline_material_path(resolved, snapshot, action="list")
        selected_fields = _normalize_entry_fields(fields)
        if limit < 0:
            raise ValueError("limit must be >= 0")
        if mode == "glob" and glob is None:
            raise ValueError("mode='glob' requires a glob pattern")
        if mode != "manifest" and not resolved.is_dir():
            raise FileNotFoundError(f"Not a directory: {resolved}")

        if mode == "manifest" and resolved.is_file():
            target = _entry_info(resolved, fields=selected_fields)
            return _hide_pipeline_materials(
                {
                    "path": str(resolved),
                    "mode": mode,
                    "fields": list(selected_fields),
                    "target": target,
                    "summary": {
                        "target_type": "file",
                        "files": 1,
                        "dirs": 0,
                        "total_size": int(resolved.stat().st_size),
                    },
                    "truncated": False,
                },
                snapshot,
            )

        entries, truncated = _collect_directory_entries(
            resolved,
            recursive=recursive,
            glob=glob,
            limit=limit,
        )
        if not snapshot.cfg.nextflow.expose_pipeline_materials:
            entries = _filter_hidden_pipeline_material_entries(entries, snapshot)
        filtered_entries = [_entry_info(entry, fields=selected_fields) for entry in entries]

        payload = {
            "path": str(resolved),
            "mode": mode,
            "fields": list(selected_fields),
            "count": len(filtered_entries),
            "entries": filtered_entries,
            "truncated": truncated,
        }
        if mode == "manifest":
            payload["target"] = _entry_info(resolved, fields=selected_fields)
            payload["summary"] = _build_manifest_summary(entries)
        return _hide_pipeline_materials(payload, snapshot)

    @mcp.tool
    @structured_tool
    def fs_read(
        path: Annotated[
            str,
            (
                "File to read on the nextmcp server filesystem. "
                "Use an absolute server path or make it relative to `cwd`."
            ),
        ],
        cwd: Annotated[
            str | None,
            SERVER_CWD_DESCRIPTION,
        ] = None,
        start_line: Annotated[
            int | None,
            "First 1-based line to return. Ignored when `tail` is provided.",
        ] = None,
        end_line: Annotated[
            int | None,
            "Last 1-based line to return. Ignored when `tail` is provided.",
        ] = None,
        tail: Annotated[
            int | None,
            "Return only the last N lines. This overrides `start_line` and `end_line`.",
        ] = None,
        max_bytes: Annotated[int, "Maximum bytes to read before truncating content."] = 262144,
    ) -> dict[str, Any]:
        """Read text content from one allowed file.

        This reads a server-side file path. Do not pass a client-local path.

        Use this for log files exposed as filesystem paths or output inspection
        after `fs_list`. If `server_info().nextflow.pipeline_materials.enabled`
        is false, configured pipeline repository files cannot be read through
        this tool. Pipeline-source reads belong to authoring servers that
        explicitly expose pipeline materials.

        Returns `ok: true` with the resolved server `path`, original `size`,
        `total_lines`, a `truncated` flag, and the selected `content`.
        """
        snapshot = runtime.snapshot()
        guard = snapshot.guard
        resolved = guard.resolve_read(path, cwd)
        _reject_hidden_pipeline_material_path(resolved, snapshot, action="read")
        if not resolved.is_file():
            raise FileNotFoundError(f"Not a file: {resolved}")

        size = resolved.stat().st_size
        if size > max_bytes:
            raw = resolved.read_bytes()[:max_bytes]
            content = raw.decode("utf-8", errors="replace")
            truncated = True
        else:
            content = resolved.read_text(errors="replace")
            truncated = False

        lines = content.splitlines(keepends=True)
        total_lines = len(lines)

        if tail is not None:
            lines = lines[-tail:]
            start_line = max(1, total_lines - tail + 1)
            end_line = total_lines
        elif start_line is not None or end_line is not None:
            s = (start_line or 1) - 1
            e = end_line or total_lines
            lines = lines[s:e]
        else:
            start_line = 1
            end_line = total_lines

        payload = {
            "path": str(resolved),
            "size": size,
            "total_lines": total_lines,
            "truncated": truncated,
            "content": "".join(lines),
        }
        return _hide_pipeline_materials(payload, snapshot)

    @mcp.tool
    @structured_tool
    def fs_write(
        path: Annotated[
            str,
            (
                "Destination file on the nextmcp server filesystem. "
                "Use an absolute server path or make it relative to `cwd`."
            ),
        ],
        content: Annotated[str, "UTF-8 text content to write or append."],
        cwd: Annotated[
            str | None,
            SERVER_CWD_DESCRIPTION,
        ] = None,
        append: Annotated[bool, "If true, append instead of overwriting the file."] = False,
        create_parents: Annotated[
            bool,
            "If true, create missing parent directories before writing.",
        ] = False,
    ) -> dict[str, Any]:
        """Write or append UTF-8 text under an allowed write root.

        All paths are resolved on the nextmcp server. Do not pass a
        client-local destination. If `server_info().nextflow.pipeline_materials.enabled`
        is false, configured pipeline repository paths cannot be modified
        through this tool.

        Prefer `fs_list` or `fs_read` first so you do not overwrite the wrong
        target. Mutating filesystem tools reject symlink targets instead of
        following them.

        Returns `ok: true` with the resolved server `path`, whether the file was
        `created`, whether content was `appended`, `bytes_written`, and final
        `size`.
        """
        snapshot = runtime.snapshot()
        guard = snapshot.guard
        resolved = guard.resolve_write(path, cwd)
        _reject_hidden_pipeline_material_path(resolved, snapshot, action="write")
        _reject_symlink(resolved, "write")
        _ensure_parent_directory(resolved, create_parents=create_parents)

        existed = resolved.exists()
        mode = "a" if append else "w"
        with resolved.open(mode, encoding="utf-8") as handle:
            handle.write(content)

        return {
            "path": str(resolved),
            "created": not existed,
            "appended": append,
            "bytes_written": len(content.encode("utf-8")),
            "size": resolved.stat().st_size,
        }

    @mcp.tool
    @structured_tool
    def fs_mkdir(
        path: Annotated[
            str,
            (
                "Directory to create on the nextmcp server filesystem. "
                "Use an absolute server path or make it relative to `cwd`."
            ),
        ],
        cwd: Annotated[
            str | None,
            SERVER_CWD_DESCRIPTION,
        ] = None,
        parents: Annotated[bool, "If true, create missing parent directories."] = True,
        exist_ok: Annotated[
            bool,
            "If true, treat an existing directory as a success instead of an error.",
        ] = True,
    ) -> dict[str, Any]:
        """Create a directory under an allowed write root.

        All paths are resolved on the nextmcp server. Do not pass a
        client-local directory path. If `server_info().nextflow.pipeline_materials.enabled`
        is false, configured pipeline repository paths cannot be modified
        through this tool.

        Use this before `fs_write`, `fs_copy`, or `nextflow_run` when the
        target workspace does not exist yet. Mutating filesystem tools reject
        symlink targets instead of following them.

        Returns `ok: true` with the resolved server `path` and whether it was newly
        `created`.
        """
        snapshot = runtime.snapshot()
        guard = snapshot.guard
        resolved = guard.resolve_write(path, cwd)
        _reject_hidden_pipeline_material_path(resolved, snapshot, action="mkdir")
        _reject_symlink(resolved, "mkdir")

        existed = resolved.exists()
        resolved.mkdir(parents=parents, exist_ok=exist_ok)

        return {
            "path": str(resolved),
            "created": not existed,
        }

    @mcp.tool
    @structured_tool
    def fs_copy(
        src: Annotated[
            str,
            (
                "Source file or directory on the nextmcp server filesystem. "
                "Use an absolute server path or make it relative to `cwd`."
            ),
        ],
        dst: Annotated[
            str,
            (
                "Destination path on the nextmcp server under an allowed write "
                "root. Relative paths use `cwd`."
            ),
        ],
        cwd: Annotated[
            str | None,
            SERVER_CWD_DESCRIPTION,
        ] = None,
        recursive: Annotated[
            bool,
            "Required when copying a directory tree.",
        ] = False,
        overwrite: Annotated[
            bool,
            "If true, replace an existing destination after validation.",
        ] = False,
        create_parents: Annotated[
            bool,
            "If true, create missing destination parent directories.",
        ] = False,
    ) -> dict[str, Any]:
        """Copy a file or directory into an allowed write root.

        All paths are resolved on the nextmcp server. Do not pass client-local
        source or destination paths. If `server_info().nextflow.pipeline_materials.enabled`
        is false, configured pipeline repository paths cannot be copied from or
        into through this tool.

        Use `fs_list` or `fs_read` first when you need to confirm the source or
        destination. Directory copies require `recursive=true`. Mutating
        filesystem tools reject symlink targets instead of following them.

        Returns `ok: true` with the resolved server `source`, `destination`, and
        copied entry `type`.
        """
        snapshot = runtime.snapshot()
        guard = snapshot.guard
        source = guard.check_read(guard.resolve(src, cwd, follow_final_symlink=False))
        destination = guard.resolve_write(dst, cwd)
        _reject_hidden_pipeline_material_path(source, snapshot, action="copy")
        _reject_hidden_pipeline_material_path(destination, snapshot, action="copy")

        _reject_symlink(source, "copy source")
        _ensure_exists(source)
        _reject_symlink(destination, "copy destination")
        _ensure_distinct_paths(source, destination)
        _ensure_not_nested_destination(source, destination)
        _ensure_parent_directory(destination, create_parents=create_parents)
        _prepare_destination(destination, overwrite=overwrite)

        if source.is_dir():
            if not recursive:
                raise IsADirectoryError(f"Directory copy requires recursive=True: {source}")
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)

        return {
            "source": str(source),
            "destination": str(destination),
            "copied": True,
            "type": _entry_type(source),
        }

    @mcp.tool
    @structured_tool
    def fs_move(
        src: Annotated[
            str,
            "Source file or directory on the nextmcp server under an allowed write root.",
        ],
        dst: Annotated[
            str,
            (
                "Destination path on the nextmcp server under an allowed write "
                "root. Relative paths use `cwd`."
            ),
        ],
        cwd: Annotated[
            str | None,
            SERVER_CWD_DESCRIPTION,
        ] = None,
        overwrite: Annotated[
            bool,
            "If true, replace an existing destination after validation.",
        ] = False,
        create_parents: Annotated[
            bool,
            "If true, create missing destination parent directories.",
        ] = False,
    ) -> dict[str, Any]:
        """Move a file or directory between allowed write roots.

        All paths are resolved on the nextmcp server. Do not pass client-local
        source or destination paths. If `server_info().nextflow.pipeline_materials.enabled`
        is false, configured pipeline repository paths cannot be moved from or
        into through this tool.

        Use `fs_list` or `fs_read` first when you need to confirm the source or
        destination. Mutating filesystem tools reject symlink targets instead
        of following them.

        Returns `ok: true` with the resolved server `source`, `destination`,
        and moved entry `type`.
        """
        snapshot = runtime.snapshot()
        guard = snapshot.guard
        source = guard.resolve_write(src, cwd)
        destination = guard.resolve_write(dst, cwd)
        _reject_hidden_pipeline_material_path(source, snapshot, action="move")
        _reject_hidden_pipeline_material_path(destination, snapshot, action="move")

        _reject_symlink(source, "move source")
        _ensure_exists(source)
        _reject_symlink(destination, "move destination")
        _ensure_distinct_paths(source, destination)
        _ensure_not_nested_destination(source, destination)
        _ensure_parent_directory(destination, create_parents=create_parents)
        _prepare_destination(destination, overwrite=overwrite)

        entry_type = _entry_type(source)
        shutil.move(str(source), str(destination))

        return {
            "source": str(source),
            "destination": str(destination),
            "moved": True,
            "type": entry_type,
        }


def _collect_directory_entries(
    resolved: Path,
    *,
    recursive: bool,
    glob: str | None,
    limit: int,
) -> tuple[list[Path], bool]:
    """Collect directory entries with optional recursion and glob filtering."""
    entries: list[Path] = []
    truncated = False
    if recursive:
        for root, dirs, files in os.walk(resolved):
            for name in dirs + files:
                if len(entries) >= limit:
                    truncated = True
                    break
                if glob and not fnmatch.fnmatch(name, glob):
                    continue
                entries.append(Path(root) / name)
            if truncated:
                break
    else:
        for item in sorted(resolved.iterdir()):
            if len(entries) >= limit:
                truncated = True
                break
            if glob and not fnmatch.fnmatch(item.name, glob):
                continue
            entries.append(item)
    return entries, truncated


def _entry_info(
    p: Path,
    *,
    fields: tuple[Literal["name", "path", "type", "size", "mtime"], ...] | None = None,
) -> dict[str, Any]:
    """Build a compact entry dict for a path."""
    selected_fields = fields or _normalize_entry_fields(None)
    try:
        st = p.stat()
        payload = {
            "name": p.name,
            "path": str(p),
            "type": "dir" if p.is_dir() else "file",
            "size": st.st_size if p.is_file() else None,
            "mtime": _isoformat_timestamp(st.st_mtime),
        }
        return {field: payload[field] for field in selected_fields}
    except OSError:
        payload = {
            "name": p.name,
            "path": str(p),
            "type": "unknown",
            "size": None,
            "mtime": None,
        }
        return {field: payload[field] for field in selected_fields}


def _entry_type(path: Path) -> str:
    """Return a stable entry type string."""
    return "dir" if path.is_dir() else "file"


def _normalize_entry_fields(
    fields: list[Literal["name", "path", "type", "size", "mtime"]] | None,
) -> tuple[Literal["name", "path", "type", "size", "mtime"], ...]:
    """Validate and normalize requested filesystem entry fields."""
    if fields is None:
        return FS_ENTRY_FIELDS

    normalized: list[Literal["name", "path", "type", "size", "mtime"]] = []
    for field in fields:
        if field not in FS_ENTRY_FIELDS:
            raise ValueError(f"Unsupported fs_list field: {field}")
        if field not in normalized:
            normalized.append(field)
    return tuple(normalized)


def _build_manifest_summary(entries: list[Path]) -> dict[str, int | str]:
    """Build a compact aggregate summary for manifest mode."""
    file_count = 0
    dir_count = 0
    total_size = 0
    for entry in entries:
        if entry.is_dir():
            dir_count += 1
            continue
        file_count += 1
        try:
            total_size += int(entry.stat().st_size)
        except OSError:
            continue

    return {
        "target_type": "dir",
        "files": file_count,
        "dirs": dir_count,
        "total_size": total_size,
    }


def _isoformat_timestamp(timestamp: float) -> str:
    """Convert a POSIX timestamp into an ISO8601 UTC string."""
    return (
        datetime.fromtimestamp(timestamp, tz=timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def _reject_symlink(path: Path, operation: str) -> None:
    """Reject symlink paths for mutating operations."""
    if path.is_symlink():
        raise ValueError(f"Refusing to {operation} via symlink: {path}")


def _ensure_exists(path: Path) -> None:
    """Raise FileNotFoundError when a path does not exist."""
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")


def _ensure_parent_directory(path: Path, *, create_parents: bool) -> None:
    """Ensure a destination parent directory exists."""
    parent = path.parent
    if parent.exists():
        if not parent.is_dir():
            raise NotADirectoryError(f"Parent is not a directory: {parent}")
        return

    if not create_parents:
        raise FileNotFoundError(f"Parent directory does not exist: {parent}")

    parent.mkdir(parents=True, exist_ok=True)


def _prepare_destination(path: Path, *, overwrite: bool) -> None:
    """Validate or clear an existing destination path."""
    _reject_symlink(path, "overwrite destination")
    if not path.exists():
        return
    if not overwrite:
        raise FileExistsError(f"Destination already exists: {path}")
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def _ensure_distinct_paths(source: Path, destination: Path) -> None:
    """Reject no-op copies/moves."""
    if source == destination:
        raise ValueError("Source and destination must be different")


def _ensure_not_nested_destination(source: Path, destination: Path) -> None:
    """Reject directory copies/moves into their own descendants."""
    if not source.exists() or not source.is_dir():
        return
    try:
        destination.relative_to(source)
    except ValueError:
        return
    raise ValueError(f"Destination cannot be inside the source directory: {destination}")


def _reject_hidden_pipeline_material_path(path: Path, snapshot: Any, *, action: str) -> None:
    """Reject direct filesystem access to hidden pipeline material paths."""
    if snapshot.cfg.nextflow.expose_pipeline_materials:
        return
    assert_not_pipeline_material_path(
        path,
        resolve_pipeline_roots(snapshot.cfg.nextflow.pipeline_roots),
        action=action,
    )


def _filter_hidden_pipeline_material_entries(entries: list[Path], snapshot: Any) -> list[Path]:
    """Remove hidden pipeline material paths from directory listings."""
    pipeline_roots = resolve_pipeline_roots(snapshot.cfg.nextflow.pipeline_roots)
    return [
        entry
        for entry in entries
        if not any(_path_is_under(entry, root) for root in pipeline_roots)
    ]


def _hide_pipeline_materials(payload: dict[str, Any], snapshot: Any) -> dict[str, Any]:
    """Redact pipeline-root paths when pipeline materials are not exposed."""
    if snapshot.cfg.nextflow.expose_pipeline_materials:
        return payload
    return cast(
        dict[str, Any],
        redact_pipeline_materials(
            payload,
            resolve_pipeline_roots(snapshot.cfg.nextflow.pipeline_roots),
        ),
    )


def _path_is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root)
    except ValueError:
        return False
    return True
