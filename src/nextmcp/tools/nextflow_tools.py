"""Thin Nextflow wrapper tools."""

from __future__ import annotations

from typing import Annotated, Any, Literal, cast

from fastmcp import FastMCP

from nextmcp.nextflow_catalog import NextflowPipelineCatalog
from nextmcp.pipeline_visibility import redact_pipeline_materials, resolve_pipeline_roots
from nextmcp.runtime_state import RuntimeState
from nextmcp.tool_response import StructuredToolError, structured_tool


def register_nextflow_tools(mcp: FastMCP, runtime: RuntimeState) -> None:
    """Register thin Nextflow wrapper tools on the MCP server."""

    @mcp.tool
    @structured_tool
    def nextflow_list_pipelines() -> dict[str, Any]:
        """List server-local Nextflow pipelines discovered under configured roots.

        Use this only when the configured pipeline ID is still unknown. This
        is a small discovery tool, not a substitute for a pipeline expert
        skill.

        If `server_info().nextflow.pipeline_materials.enabled` is false,
        returned records only identify runnable pipelines and do not include
        pipeline repository paths or schema-derived metadata.

        Returns `ok: true` with a `count` and a `pipelines` array.
        """
        snapshot = runtime.snapshot()
        catalog = _require_catalog(snapshot.nextflow_catalog)
        pipelines = [
            item.to_summary_dict(include_materials=snapshot.cfg.nextflow.expose_pipeline_materials)
            for item in catalog.list_pipelines()
        ]
        return {
            "count": len(pipelines),
            "pipelines": pipelines,
        }

    @mcp.tool
    @structured_tool
    def nextflow_inspect_pipeline(
        pipeline: Annotated[
            str,
            "Configured pipeline ID or explicit server-local pipeline path.",
        ],
        cwd: Annotated[
            str | None,
            "Server-side working directory used to resolve relative pipeline paths.",
        ] = None,
        detail: Annotated[
            Literal["summary", "materials"],
            (
                "Call only when `server_info().nextflow.pipeline_materials.enabled` "
                "is true. Use `summary` for a compact authoring manifest or "
                "`materials` to inline README/docs/source content for "
                "expert-skill generation."
            ),
        ] = "summary",
    ) -> dict[str, Any]:
        """Fetch one server-local pipeline manifest or authoring materials.

        This is an authoring and package-maintenance tool for local pipelines.
        Before calling it, check `server_info().nextflow.pipeline_materials.enabled`.
        If that value is false, do not call this tool for ordinary runtime
        planning. Use the configured pipeline ID with `nextflow_run` and rely
        on the pipeline expert skill instead.

        Returns `ok: true` with an inspect payload containing repository paths,
        schema summaries, documents, and source files. Materials mode also
        inlines the full parsed `schema` plus `content` for `documents` and
        `source_files`.
        """
        snapshot = runtime.snapshot()
        if not snapshot.cfg.nextflow.expose_pipeline_materials:
            raise StructuredToolError(
                error_code="feature_disabled",
                message="Pipeline authoring materials are not exposed by this server.",
                suggestions=(
                    "Use the configured pipeline ID with nextflow_run for ordinary runtime work.",
                    "Check server_info().nextflow.pipeline_materials.enabled before calling "
                    "this tool.",
                ),
            )
        catalog = _require_catalog(snapshot.nextflow_catalog)
        return catalog.inspect_pipeline(pipeline, cwd, detail=detail)

    @mcp.tool
    @structured_tool
    def nextflow_run(
        pipeline: Annotated[
            str | None,
            (
                "Configured pipeline ID or remote pipeline identifier. Explicit "
                "server-local pipeline script paths are accepted only when the "
                "path is already known. Required unless `from_run_id` is provided."
            ),
        ] = None,
        project: Annotated[
            str | None,
            (
                "Project identifier used to place this run under the configured "
                "projects root. Required unless `from_run_id` is provided."
            ),
        ] = None,
        from_run_id: Annotated[
            str | None,
            (
                "Optional source run identifier. This is the only public "
                "resume route. nextmcp reuses the original run root and "
                "resumes that run before applying local overrides."
            ),
        ] = None,
        run_id: Annotated[
            str | None,
            "Optional explicit run identifier. Do not pass this with `from_run_id`.",
        ] = None,
        run_name: Annotated[
            str | None,
            "Optional human-readable name stored with the run record.",
        ] = None,
        entry: Annotated[str | None, "Optional Nextflow entry workflow name."] = None,
        params: Annotated[
            dict[str, Any] | None,
            (
                "Optional Nextflow params passed as CLI `--key value` pairs. "
                "Use this for ordinary pipeline params such as inputs, references, "
                "route selectors, and tool-specific extra_* settings, not for "
                "resource-cap overrides that must stay in a Nextflow config file."
            ),
        ] = None,
        profile: Annotated[
            str | None,
            "Optional Nextflow profile string. If omitted, use `nextflow.default_profile`.",
        ] = None,
        config_files: Annotated[
            str | list[str] | None,
            (
                "Optional Nextflow config file path or list of config files on "
                "the server. Relative paths use the project root. Use this for "
                "site/runtime configs and small server-local override configs "
                "for settings that must stay in config scope, such as "
                "`max_cpus`, `max_memory`, and `max_time`."
            ),
        ] = None,
        extra_args: Annotated[
            list[str] | None,
            "Additional raw CLI arguments appended after the normalized Nextflow arguments.",
        ] = None,
        env: Annotated[
            dict[str, str] | None,
            "Optional environment overrides merged on top of server-side Nextflow environment.",
        ] = None,
        prepare: Annotated[
            bool,
            (
                "If true, resolve the final Nextflow launch plan and return it without starting "
                "the task."
            ),
        ] = False,
        validate_params_schema: Annotated[
            bool,
            (
                "If true, validate CLI `params` against a local `nextflow_schema.json` using "
                "generic required/type/default checks before launch. Public responses redact "
                "schema file paths when pipeline materials are hidden."
            ),
        ] = False,
        detach: Annotated[
            bool,
            "If true, return immediately after launch. If false, wait for completion.",
        ] = True,
    ) -> dict[str, Any]:
        """Launch or prepare a Nextflow pipeline in a project-owned run directory.

        For a new run, provide `project` and `pipeline`. To restart a stored run, provide
        `from_run_id`; in that mode do not pass `project`, `pipeline`, or `run_id`.
        All paths refer to the nextmcp server filesystem. Relative `config_files` and
        path-like `params` are resolved from the project root.

        Use `params` for workflow-facing options and `config_files` for Nextflow config
        files or site/runtime override files. Use `extra_args` only when no normalized
        field covers the needed Nextflow CLI flag.

        Set `prepare=true` to return the normalized launch plan, path checks, resume
        hints, expected artifact paths, and run layout without starting Nextflow. Set
        `validate_params_schema=true` only for local pipelines with `nextflow_schema.json`;
        this performs generic schema checks, not workflow-specific rules.

        If `server_info().nextflow.pipeline_materials.enabled` is false, public
        responses redact pipeline repository paths and schema file paths.
        Returns a compact run summary.
        """
        snapshot = runtime.snapshot()
        normalized_config_files = _normalize_optional_string_list(
            config_files,
            field_name="config_files",
        )
        return _hide_pipeline_materials(
            snapshot.project_run_manager.nextflow_run(
                executable=snapshot.cfg.nextflow.executable,
                pipeline=pipeline,
                project=project,
                from_run_id=from_run_id,
                run_id=run_id,
                run_name=run_name,
                entry=entry,
                params=params,
                profile=profile,
                config_files=normalized_config_files,
                extra_args=extra_args,
                env={**snapshot.cfg.nextflow.env, **(env or {})},
                prepare=prepare,
                validate_params_schema=validate_params_schema,
                detach=detach,
            ),
            snapshot,
        )


def _require_catalog(catalog: NextflowPipelineCatalog | None) -> NextflowPipelineCatalog:
    """Require a configured server-local pipeline catalog."""
    if catalog is None:
        raise ValueError("nextflow.pipeline_roots is empty")
    return catalog


def _normalize_optional_string_list(
    value: str | list[str] | None,
    *,
    field_name: str,
) -> list[str] | None:
    """Accept one string or a list of non-empty strings for tool inputs."""
    if value is None:
        return None
    if isinstance(value, str):
        if not value:
            raise ValueError(
                f"{field_name} must be a non-empty string or a list of non-empty strings"
            )
        return [value]

    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise ValueError(
                f"{field_name} must be a non-empty string or a list of non-empty strings"
            )
        normalized.append(item)
    return normalized


def _hide_pipeline_materials(payload: dict[str, Any], snapshot: Any) -> dict[str, Any]:
    """Redact pipeline-root paths when pipeline materials are not exposed."""
    if snapshot.cfg.nextflow.expose_pipeline_materials:
        return payload
    redacted = redact_pipeline_materials(
        payload,
        resolve_pipeline_roots(snapshot.cfg.nextflow.pipeline_roots),
    )
    return cast(
        dict[str, Any],
        _hide_schema_available_defaults(redacted),
    )


def _hide_schema_available_defaults(value: Any) -> Any:
    """Remove schema-derived defaults from public payloads."""
    if isinstance(value, dict):
        return {
            key: _hide_schema_available_defaults(item)
            for key, item in value.items()
            if key != "available_defaults"
        }
    if isinstance(value, list):
        return [_hide_schema_available_defaults(item) for item in value]
    if isinstance(value, tuple):
        return [_hide_schema_available_defaults(item) for item in value]
    return value
