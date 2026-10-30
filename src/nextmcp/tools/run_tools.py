"""Run inspection and control tools."""

from __future__ import annotations

from typing import Annotated, Any, Literal, Sequence, cast

from fastmcp import FastMCP

from nextmcp.pipeline_visibility import redact_pipeline_materials, resolve_pipeline_roots
from nextmcp.runtime_state import RuntimeState
from nextmcp.tool_response import structured_tool


def register_run_tools(mcp: FastMCP, runtime: RuntimeState) -> None:
    """Register project-run tools on the MCP server."""

    @mcp.tool
    @structured_tool
    def run_list(
        project: Annotated[
            str | None,
            (
                "Optional exact project filter. Use this first when the user is "
                "working inside one project."
            ),
        ] = None,
        pipeline: Annotated[
            str | None,
            "Optional exact Nextflow pipeline filter.",
        ] = None,
        status: Annotated[
            str | None,
            (
                "Optional status filter such as `prepared`, `running`, "
                "`succeeded`, `failed`, or `stopped`."
            ),
        ] = None,
        run_name_contains: Annotated[
            str | None,
            "Optional substring match against the stored run name.",
        ] = None,
        artifact_path_contains: Annotated[
            str | None,
            "Optional substring match against indexed artifact paths for launched runs.",
        ] = None,
        finished_after: Annotated[
            str | None,
            "Optional inclusive lower bound for `finished_at` in ISO8601 UTC form.",
        ] = None,
        finished_before: Annotated[
            str | None,
            "Optional inclusive upper bound for `finished_at` in ISO8601 UTC form.",
        ] = None,
        detail: Annotated[
            Literal["summary", "full"],
            (
                "Response detail level. Use `summary` for history browsing and "
                "`full` only when you need stored run layout. Hidden pipeline "
                "repository paths are redacted from both views."
            ),
        ] = "summary",
        limit: Annotated[int, "Maximum number of runs to return."] = 100,
        offset: Annotated[int, "Result offset for pagination."] = 0,
    ) -> dict[str, Any]:
        """List known runs, usually narrowed to one project.

        Use this when you need to rediscover a `run_id`, filter by status, or
        browse run history for one project before calling `run_get`,
        `run_logs`, or `run_artifacts`. The default `detail="summary"` keeps
        the list small. Ask for `detail="full"` only when you need stored
        layout paths in the list itself. When pipeline materials are hidden,
        pipeline repository paths are redacted from returned records.

        Returns `ok: true` with pagination metadata and a `runs` array.
        """
        snapshot = runtime.snapshot()
        return _hide_pipeline_materials(
            snapshot.project_run_manager.list_runs(
                project=project,
                pipeline=pipeline,
                status=status,
                run_name_contains=run_name_contains,
                artifact_path_contains=artifact_path_contains,
                finished_after=finished_after,
                finished_before=finished_before,
                detail=detail,
                limit=limit,
                offset=offset,
            ),
            snapshot,
        )

    @mcp.tool
    @structured_tool
    def run_get(
        run_id: Annotated[
            str,
            "Run identifier returned by `nextflow_run` or listed by `run_list`.",
        ],
        include: Annotated[
            Sequence[Literal["progress", "artifact_summary", "diagnosis", "next_actions"]] | None,
            (
                "Optional extra sections. Leave this empty for routine status polling "
                "so the response stays small."
            ),
        ] = None,
        detail: Annotated[
            Literal["summary", "full"],
            (
                "Response detail level. Use `summary` for routine polling and "
                "`full` when you need run-owned server-side paths, run layout, "
                "or the hidden process ID. Hidden pipeline repository paths are redacted."
            ),
        ] = "summary",
    ) -> dict[str, Any]:
        """Inspect one run and optionally include compact diagnosis sections.

        Call this first when diagnosing a workflow run so you can confirm
        `status`, timestamps, and the basic launch metadata before reading raw
        logs or browsing artifacts. The default `detail="summary"` keeps
        polling small. Ask for `detail="full"` only when you need the
        server-side project root, run root, results/work/job directories, or
        `run_layout`. The full view also exposes `launch_spec`,
        `nextflow_session_uuid`, and structured resume-compatibility fields for
        `from_run_id` restart planning. When pipeline materials are hidden,
        pipeline repository paths are redacted from both summary and full
        records.

        Returns `ok: true` with either a summary or full run record.
        """
        snapshot = runtime.snapshot()
        return _hide_pipeline_materials(
            snapshot.project_run_manager.get_run(
                run_id,
                include=include or [],
                detail=detail,
            ),
            snapshot,
        )

    @mcp.tool
    @structured_tool
    def run_artifacts(
        run_id: Annotated[
            str,
            "Run identifier returned by `nextflow_run` or listed by `run_list`.",
        ],
        section: Annotated[
            Literal["record_files", "declared_outputs", "published_roots", "items"],
            (
                "Artifact section to inspect. Use `record_files` for run-owned logs and JSON, "
                "`declared_outputs` for expected outputs, `published_roots` for result roots, "
                "and `items` for scanned artifact entries."
            ),
        ],
        root_label: Annotated[
            str | None,
            'Optional published-root label filter. Only supported when `section="items"`.',
        ] = None,
        path_contains: Annotated[
            str | None,
            "Optional substring filter across artifact path-like fields.",
        ] = None,
        detail: Annotated[
            Literal["auto", "compact", "full"],
            (
                "Response detail level. `auto` keeps the default response small. "
                "Hidden pipeline repository paths are redacted from all views."
            ),
        ] = "auto",
        limit: Annotated[
            int,
            "Maximum number of artifact entries to return. Defaults to 50 and is capped at 200.",
        ] = 50,
        offset: Annotated[int, "Result offset for artifact pagination."] = 0,
    ) -> dict[str, Any]:
        """Read one artifact section for one run with filtering and pagination.

        Use `run_get(run_id, include=[\"artifact_summary\"])` first so you know
        which sections are available. This tool returns one section at a time
        to keep responses small.

        Returns `ok: true` with the requested section, filters, and `items`.
        """
        snapshot = runtime.snapshot()
        return _hide_pipeline_materials(
            snapshot.project_run_manager.get_run_artifacts(
                run_id,
                section=section,
                root_label=root_label,
                path_contains=path_contains,
                detail=detail,
                limit=limit,
                offset=offset,
            ),
            snapshot,
        )

    @mcp.tool
    @structured_tool
    def run_logs(
        run_id: Annotated[
            str,
            "Run identifier returned by `nextflow_run` or listed by `run_list`.",
        ],
        stream: Annotated[
            Literal["stdout", "stderr", "nextflow"],
            (
                "Which log stream to inspect. `nextflow` is the default because "
                "it is the most useful first diagnostic layer for workflow runs."
            ),
        ] = "nextflow",
        view: Annotated[
            Literal["important", "raw"],
            (
                "Response mode. `important` returns a compact summary first; "
                "use `raw` only when you need log lines. Hidden pipeline "
                "repository paths are redacted even in raw mode."
            ),
        ] = "important",
        after_line: Annotated[
            int | None,
            (
                "Return only lines strictly after this 1-based line number and "
                'include `next_after_line`. Only used with `view="raw"`.'
            ),
        ] = None,
        start_line: Annotated[
            int | None,
            "Optional inclusive 1-based start line for an explicit raw range read.",
        ] = None,
        end_line: Annotated[
            int | None,
            "Optional inclusive 1-based end line for an explicit raw range read.",
        ] = None,
        tail: Annotated[
            int | None,
            (
                'When `view="raw"` and no range is given, return only the '
                "last N lines. Use 0 to disable the default raw tail."
            ),
        ] = 50,
    ) -> dict[str, Any]:
        """Inspect one run log stream in compact or raw form.

        Use `run_get(run_id)` first if you only need the current status. The
        default `stream="nextflow"` plus `view="important"` returns a compact
        framework-first summary and, on task failures, may add a small excerpt
        from `.command.err` or `stderr.log`. Switch to `view="raw"` only when
        you need stdout, stderr, or Nextflow framework log lines. In raw mode,
        `after_line` supports incremental fetches during long runs. When
        pipeline materials are hidden, pipeline repository paths are redacted
        even from raw log content.

        Returns `ok: true` with either a compact summary or raw line-sliced
        content, plus `run_id`.
        """
        snapshot = runtime.snapshot()
        return _hide_pipeline_materials(
            snapshot.project_run_manager.read_run_logs(
                run_id,
                stream=stream,
                view=view,
                after_line=after_line,
                start_line=start_line,
                end_line=end_line,
                tail=tail,
            ),
            snapshot,
        )

    @mcp.tool
    @structured_tool
    def run_stop(
        run_id: Annotated[
            str,
            "Run identifier returned by `nextflow_run` or listed by `run_list`.",
        ],
        force: Annotated[
            bool,
            (
                "If true, force-stop the underlying process group instead of "
                "sending a graceful request first."
            ),
        ] = False,
    ) -> dict[str, Any]:
        """Request one active run to stop.

        Use this when the workflow should stop but you still want the run
        record to remain available for later inspection.

        Returns `ok: true` with the updated run summary.
        """
        snapshot = runtime.snapshot()
        return _hide_pipeline_materials(
            snapshot.project_run_manager.stop_run(run_id, force=force),
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
