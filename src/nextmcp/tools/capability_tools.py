"""Read-only server capability discovery tools."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, cast

from fastmcp import FastMCP

from nextmcp.config import resolve_projects_root
from nextmcp.pipeline_visibility import redact_pipeline_materials, resolve_pipeline_roots
from nextmcp.runtime_state import RuntimeSnapshot, RuntimeState
from nextmcp.tool_response import structured_tool


def register_capability_tools(mcp: FastMCP, runtime: RuntimeState) -> None:
    """Register read-only capability discovery tools on the MCP server."""

    @mcp.tool
    @structured_tool
    def server_info() -> dict[str, Any]:
        """Return a safe read-only summary of the current server environment.

        Call this first when the deployment-specific server layout is unknown
        and you need to learn the current read/write roots, projects root, and
        Nextflow runtime policy without reading `config.yaml` directly. All
        returned paths refer to the nextmcp server filesystem, not the client
        machine. Use `nextflow_list_pipelines` after this only when the
        concrete local pipeline ID is still unknown. If
        `nextflow.pipeline_materials.enabled` is false in this response,
        pipeline repository paths are not returned by runtime tools. If an
        expert skill already covers the pipeline, do not restart ordinary
        planning by reading pipeline source materials. The
        returned `nextflow.pipeline_materials` policy tells runtime clients
        whether authoring-time pipeline materials are exposed and explicitly
        marks that ordinary runtime work should not call that path. This tool
        also returns a compact readiness check for the configured Nextflow
        executable, projects root, state DB parent, and local pipeline
        catalog.

        Returns `ok: true` with `paths`, `projects`, `nextflow`, and `readiness`
        summaries. Secret values and `nextflow.env` contents are intentionally
        omitted.
        """
        snapshot = runtime.snapshot()
        return _hide_pipeline_materials(_server_info_payload(snapshot), snapshot)


def _server_info_payload(snapshot: RuntimeSnapshot) -> dict[str, Any]:
    """Build the read-only server capability summary."""
    cfg = snapshot.cfg
    payload: dict[str, Any] = {
        "paths": {
            "allowed_read_roots": _resolved_paths(cfg.paths.allowed_read_roots),
            "allowed_write_roots": _resolved_paths(cfg.paths.allowed_write_roots),
        },
        "projects": {
            "root": str(resolve_projects_root(cfg)),
        },
        "nextflow": {
            "default_profile": cfg.nextflow.default_profile,
            "local_pipeline_catalog": {
                "enabled": bool(cfg.nextflow.pipeline_roots),
                "configured_root_count": len(cfg.nextflow.pipeline_roots),
            },
            "pipeline_materials": {
                "enabled": cfg.nextflow.expose_pipeline_materials,
                "intended_use": "authoring_only",
                "ordinary_runtime_should_call": False,
            },
        },
        "readiness": _build_readiness_summary(snapshot),
    }
    return payload


def _hide_pipeline_materials(payload: dict[str, Any], snapshot: RuntimeSnapshot) -> dict[str, Any]:
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


def _resolved_paths(paths: list[str]) -> list[str]:
    """Resolve configured paths into stable absolute server-side strings."""
    return [str(Path(path).resolve()) for path in paths]


def _build_readiness_summary(snapshot: RuntimeSnapshot) -> dict[str, Any]:
    """Build a small run-readiness summary for the current server snapshot."""
    cfg = snapshot.cfg
    projects_root = resolve_projects_root(cfg)
    db_parent = Path(cfg.state.db_path).resolve().parent
    pipeline_roots = [Path(path).resolve() for path in cfg.nextflow.pipeline_roots]
    catalog_check = _check_local_pipeline_catalog(pipeline_roots)

    checks: dict[str, Any] = {
        "nextflow_executable": _check_executable(cfg.nextflow.executable),
        "projects_root": _check_writable_path(projects_root, include_path=False),
        "state_db_parent": _check_writable_path(db_parent),
        "local_pipeline_catalog": catalog_check,
    }

    blocking_issues: list[str] = []
    warnings: list[str] = []

    executable_check = checks["nextflow_executable"]
    if not executable_check["available"]:
        blocking_issues.append(
            f"Configured nextflow executable is not available: {cfg.nextflow.executable}"
        )

    projects_root_check = checks["projects_root"]
    if not projects_root_check["writable"]:
        blocking_issues.append(f"Projects root is not writable: {projects_root}")

    db_parent_check = checks["state_db_parent"]
    if not db_parent_check["writable"]:
        blocking_issues.append(f"State DB parent directory is not writable: {db_parent}")

    if catalog_check["missing_root_count"] > 0:
        warnings.append(
            f"{catalog_check['missing_root_count']} configured pipeline roots do not exist."
        )
    if catalog_check["unreadable_root_count"] > 0:
        warnings.append(
            f"{catalog_check['unreadable_root_count']} configured pipeline roots are not readable."
        )

    return {
        "ok": not blocking_issues,
        "checks": checks,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
    }


def _check_executable(executable: str) -> dict[str, Any]:
    """Report whether the configured executable can be resolved."""
    candidate = Path(executable)
    resolved_path: str | None = None
    if candidate.is_absolute():
        resolved_candidate = candidate.resolve()
        resolved_path = str(resolved_candidate)
        available = resolved_candidate.is_file() and os.access(resolved_candidate, os.X_OK)
    else:
        resolved_from_path = shutil.which(executable)
        resolved_path = resolved_from_path
        available = resolved_from_path is not None

    return {
        "resolved_path": resolved_path,
        "available": available,
    }


def _check_writable_path(path: Path, *, include_path: bool = True) -> dict[str, Any]:
    """Report whether a path or its nearest existing ancestor is writable."""
    exists = path.exists()
    target = path if exists else _nearest_existing_parent(path)
    free_bytes = _free_bytes(target) if target is not None else None

    writable = False
    if exists:
        writable = path.is_dir() and os.access(path, os.W_OK | os.X_OK)
    elif target is not None:
        writable = target.is_dir() and os.access(target, os.W_OK | os.X_OK)

    payload: dict[str, Any] = {
        "exists": exists,
        "writable": writable,
        "free_bytes": free_bytes,
    }
    if include_path:
        payload["path"] = str(path)
    return payload


def _check_pipeline_root(path: Path) -> dict[str, Any]:
    """Report one configured pipeline root status."""
    exists = path.exists()
    readable = exists and path.is_dir() and os.access(path, os.R_OK | os.X_OK)
    pipeline_count = 0
    if readable:
        pipeline_count = sum(1 for child in path.iterdir() if (child / "main.nf").is_file())
    return {
        "exists": exists,
        "readable": readable,
        "pipeline_count": pipeline_count,
    }


def _check_local_pipeline_catalog(pipeline_roots: list[Path]) -> dict[str, Any]:
    """Summarize configured local pipeline catalog readiness without exposing paths."""
    root_checks = [_check_pipeline_root(path) for path in pipeline_roots]
    missing_root_count = sum(1 for item in root_checks if not item["exists"])
    unreadable_root_count = sum(
        1 for item in root_checks if item["exists"] and not item["readable"]
    )
    return {
        "enabled": bool(pipeline_roots),
        "configured_root_count": len(pipeline_roots),
        "readable_root_count": sum(1 for item in root_checks if item["readable"]),
        "missing_root_count": missing_root_count,
        "unreadable_root_count": unreadable_root_count,
        "pipeline_count": sum(int(item["pipeline_count"]) for item in root_checks),
    }


def _nearest_existing_parent(path: Path) -> Path | None:
    """Return the nearest existing ancestor for a missing path."""
    current = path
    while not current.exists():
        if current.parent == current:
            return None
        current = current.parent
    return current


def _free_bytes(path: Path) -> int | None:
    """Return filesystem free bytes for one existing path when available."""
    try:
        stats = os.statvfs(path)
    except OSError:
        return None
    return int(stats.f_bavail * stats.f_frsize)
