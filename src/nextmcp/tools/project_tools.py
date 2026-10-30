"""Project discovery tools."""

from __future__ import annotations

from typing import Annotated, Any, Literal, cast

from fastmcp import FastMCP

from nextmcp.pipeline_visibility import redact_pipeline_materials, resolve_pipeline_roots
from nextmcp.runtime_state import RuntimeState
from nextmcp.tool_response import structured_tool


def register_project_tools(mcp: FastMCP, runtime: RuntimeState) -> None:
    """Register project-oriented tools on the MCP server."""

    @mcp.tool
    @structured_tool
    def project_list(
        detail: Annotated[
            Literal["summary", "full"],
            (
                "Response detail level. Use `summary` for routine project discovery "
                "and `full` only when you need each project's stored metadata."
            ),
        ] = "summary",
    ) -> dict[str, Any]:
        """List known projects under the configured projects root.

        Use this first when the user knows the work is organized by project but
        does not know the exact `project` identifier yet. The default
        `detail="summary"` keeps discovery small and returns each project's ID,
        root, and timestamps. Ask for `detail="full"` only when you need the
        stored project metadata itself. Full project responses follow the same
        pipeline material redaction policy as run tools.

        Returns `ok: true` with a `count` and a `projects` array.
        """
        snapshot = runtime.snapshot()
        return _hide_pipeline_materials(
            snapshot.project_run_manager.list_projects(detail=detail),
            snapshot,
        )

    @mcp.tool
    @structured_tool
    def project_get(
        project: Annotated[
            str,
            "Project identifier returned by `project_list` or chosen for `nextflow_run`.",
        ],
        detail: Annotated[
            Literal["summary", "full"],
            (
                "Response detail level. Use `summary` for one project record and "
                "`full` when you also need recent runs under that project."
            ),
        ] = "summary",
    ) -> dict[str, Any]:
        """Inspect one project and optionally include its runs.

        Call this when you already know the `project` ID and want to confirm
        the server-side project root before launching or browsing runs. The
        default `detail="summary"` returns only the project record. Use
        `detail="full"` when you also want the project's current run summaries
        in the same response. Full project responses follow the same pipeline
        material redaction policy as run tools.

        Returns `ok: true` with one project payload.
        """
        snapshot = runtime.snapshot()
        return _hide_pipeline_materials(
            snapshot.project_run_manager.get_project(project, detail=detail),
            snapshot,
        )


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
