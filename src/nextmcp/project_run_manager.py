"""Project- and run-centered Nextflow runtime helpers."""

from __future__ import annotations

import re
import shutil
import uuid
from pathlib import Path
from typing import Any, Literal, Sequence

from nextmcp.config import AppConfig, resolve_projects_root
from nextmcp.errors import ResourceNotFoundError
from nextmcp.paths import PathGuard
from nextmcp.process_runtime import (
    ProcessManager,
    _new_process_id,
    _utcnow,
    get_job_paths,
    read_json,
    write_json,
)
from nextmcp.process_store import ProcessStore

_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class ProjectRunManager:
    """Manage Nextflow runs inside project-owned directories."""

    def __init__(
        self,
        cfg: AppConfig,
        guard: PathGuard,
        store: ProcessStore,
        process_manager: ProcessManager,
    ) -> None:
        self._cfg = cfg
        self._guard = guard
        self._store = store
        self._process_manager = process_manager
        self._projects_root = resolve_projects_root(cfg)
        self._projects_root.mkdir(parents=True, exist_ok=True)

    def nextflow_run(
        self,
        *,
        executable: str,
        pipeline: str | None,
        project: str | None,
        from_run_id: str | None = None,
        run_id: str | None = None,
        run_name: str | None = None,
        entry: str | None = None,
        params: dict[str, Any] | None = None,
        profile: str | None = None,
        config_files: list[str] | None = None,
        extra_args: list[str] | None = None,
        env: dict[str, str] | None = None,
        detach: bool = True,
        prepare: bool = False,
        validate_params_schema: bool = False,
    ) -> dict[str, Any]:
        """Prepare or launch one Nextflow run inside one project layout."""
        source_payload: dict[str, Any] | None = None
        if from_run_id is not None:
            source_payload, source_run_json = self._load_run(from_run_id)
            source_payload = self._refresh_run_payload(source_payload, source_run_json)
            if source_payload.get("status") == "prepared":
                raise ValueError(
                    "Source run has not started yet and cannot be used with from_run_id"
                )
            if source_payload.get("status") == "running":
                raise ValueError(
                    "Source run is still active; stop it before starting a new launch from_run_id"
                )

            launch_spec = _build_internal_launch_spec(source_payload)
            if not launch_spec:
                raise ValueError(f"Source run {from_run_id} does not expose a launch_spec")

            source_project = str(source_payload["project_id"])
            source_pipeline = str(launch_spec["pipeline"])
            if project is not None:
                raise ValueError("from_run_id resumes the original project; do not pass `project`")
            if pipeline is not None:
                raise ValueError(
                    "from_run_id resumes the original pipeline; do not pass `pipeline`"
                )
            if run_id is not None:
                raise ValueError("from_run_id resumes the original run_id; do not pass `run_id`")

            project = source_project
            pipeline = source_pipeline
            run_id = from_run_id

            if run_name is None:
                run_name = source_payload.get("run_name")
            if entry is None:
                entry = launch_spec.get("entry")

            inherited_params = dict(launch_spec.get("params") or {})
            if params is not None:
                inherited_params.update(params)
            params = inherited_params

            if profile is None:
                profile = launch_spec.get("profile")
            if config_files is None:
                config_files = list(launch_spec.get("config_files") or [])
            if extra_args is None:
                extra_args = list(launch_spec.get("extra_args") or [])

            source_session_uuid = source_payload.get("nextflow_session_uuid")
            if not isinstance(source_session_uuid, str) or not source_session_uuid:
                raise ValueError(
                    "Source run does not expose a usable Nextflow session UUID for resume"
                )
            resume_session_id = source_session_uuid
            resume = False
        else:
            resume = False
            resume_session_id = None

        if pipeline is None:
            raise ValueError("pipeline is required unless from_run_id is provided")
        if project is None:
            raise ValueError("project is required unless from_run_id is provided")

        project_id = _validate_identifier(project, field_name="project")
        resolved_run_id = (
            _validate_identifier(run_id, field_name="run_id")
            if run_id is not None
            else _new_run_id()
        )
        project_paths = _project_paths(self._projects_root, project_id)
        run_paths = _run_paths(project_paths.project_root, resolved_run_id)

        created_project = self._ensure_project(project_paths)
        existing_run = read_json(run_paths.run_json)
        if (
            existing_run is not None
            and isinstance(existing_run.get("process_id"), str)
            and existing_run.get("status") == "running"
        ):
            raise ValueError(f"run_id is already active: {resolved_run_id}")

        prepared = self._process_manager._prepare_nextflow_run(
            executable=executable,
            pipeline=_resolve_pipeline_argument(pipeline, project_paths.project_root),
            cwd=str(run_paths.run_root),
            path_base=str(project_paths.project_root),
            entry=entry,
            params=params,
            profile=profile,
            config_files=config_files,
            work_dir=str(run_paths.work_dir),
            resume=bool(resume),
            resume_session_id=resume_session_id,
            extra_args=extra_args,
            env=env,
            validate_params_schema=validate_params_schema,
            job_paths=get_job_paths(run_paths.job_dir),
            default_results_dir=str(run_paths.results_dir),
            project_id=project_id,
            run_id=resolved_run_id,
        )
        prepared.command_extra["resume_source_run_id"] = from_run_id

        existing_job_dir = run_paths.job_dir if run_paths.job_dir.exists() else None
        prepared.resume_hint["existing_job_dir"] = (
            None if existing_job_dir is None else str(existing_job_dir)
        )
        prepared.resume_hint["job_dir_archive_on_launch"] = existing_job_dir is not None
        if source_payload is not None:
            prepared.resume_hint["source_run_id"] = from_run_id
            prepared.resume_hint["source_resume_compatible"] = bool(
                source_payload.get("resume_compatible", False)
            )
            prepared.resume_hint["source_resume_incompatible_reason"] = source_payload.get(
                "resume_incompatible_reason"
            )
            prepared.resume_hint["resume_mode"] = "from_run_id"

        if prepare:
            payload = self._build_run_payload(
                project_id=project_id,
                project_root=project_paths.project_root,
                run_id=resolved_run_id,
                run_name=run_name,
                process_id=None,
                process_record=None,
                prepared=prepared,
            )
            write_json(run_paths.run_json, payload)
            return {
                "kind": "nextflow",
                "mode": "prepare",
                "project": {
                    "project_id": project_id,
                    "project_root": str(project_paths.project_root),
                    "created": created_project,
                },
                "run": _render_run_payload(payload, detail="summary"),
                "path_checks": prepared.path_checks,
                "path_warnings": prepared.path_warnings,
                "resume_hint": prepared.resume_hint,
                "expected_artifacts": prepared.expected_artifacts,
                "run_layout": prepared.command_extra["run_layout"],
                "layout_warnings": prepared.command_extra["layout_warnings"],
                **(
                    {"schema_validation": prepared.schema_validation}
                    if prepared.schema_validation is not None
                    else {}
                ),
            }

        resume_incompatible_reason = prepared.resume_hint.get("resume_incompatible_reason")
        if prepared.resume_hint.get("requested") and isinstance(resume_incompatible_reason, str):
            raise ValueError(resume_incompatible_reason)
        if (
            source_payload is not None
            and prepared.resume_hint.get("requested")
            and not bool(source_payload.get("resume_compatible", False))
        ):
            source_reason = source_payload.get("resume_incompatible_reason")
            if isinstance(source_reason, str) and source_reason:
                raise ValueError(source_reason)

        if existing_job_dir is not None:
            prepared.command_extra["archived_job_dir"] = _archive_existing_job_dir(existing_job_dir)

        record = self._process_manager._launch_prepared_process(
            argv=prepared.argv,
            cwd=prepared.cwd,
            env=prepared.env,
            stdin=None,
            detach=detach,
            timeout_seconds=None,
            label=run_name,
            kind="nextflow",
            job_paths=prepared.job_paths,
            process_id=_new_process_id(),
            command_extra=prepared.command_extra,
            command_metadata={"pipeline_fingerprint": prepared.pipeline_fingerprint},
        )
        payload = self._build_run_payload(
            project_id=project_id,
            project_root=project_paths.project_root,
            run_id=resolved_run_id,
            run_name=run_name,
            process_id=str(record["process_id"]),
            process_record=self._process_manager.get_process(
                str(record["process_id"]),
                detail="full",
            ),
            prepared=prepared,
        )
        write_json(run_paths.run_json, payload)
        return _render_run_payload(payload, detail="summary")

    def list_projects(self, *, detail: Literal["summary", "full"] = "summary") -> dict[str, Any]:
        """List known project directories under the configured projects root."""
        projects = [_render_project_payload(item, detail=detail) for item in self._load_projects()]
        return {
            "detail": detail,
            "count": len(projects),
            "projects": projects,
        }

    def get_project(
        self,
        project: str,
        *,
        detail: Literal["summary", "full"] = "summary",
    ) -> dict[str, Any]:
        """Read one project and optionally include recent runs."""
        project_id = _validate_identifier(project, field_name="project")
        project_paths = _project_paths(self._projects_root, project_id)
        payload = _load_project(project_paths.project_json)
        if payload is None:
            raise ResourceNotFoundError(
                resource_type="project",
                resource_id=project_id,
                message=f"Unknown project: {project_id}",
            )
        if detail == "summary":
            return _render_project_payload(payload, detail=detail)

        runs = list(self._list_runs(project=project_id, detail="summary")["runs"])
        full_payload = dict(payload)
        full_payload["runs"] = runs
        full_payload["run_count"] = len(runs)
        return full_payload

    def list_runs(
        self,
        *,
        project: str | None = None,
        pipeline: str | None = None,
        status: str | None = None,
        run_name_contains: str | None = None,
        artifact_path_contains: str | None = None,
        finished_after: str | None = None,
        finished_before: str | None = None,
        detail: Literal["summary", "full"] = "summary",
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List known runs from run.json files."""
        return self._list_runs(
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
        )

    def get_run(
        self,
        run_id: str,
        *,
        include: Sequence[str] | None = None,
        detail: Literal["summary", "full"] = "summary",
    ) -> dict[str, Any]:
        """Read one run by run_id."""
        run_payload, run_json = self._load_run(run_id)
        run_payload = self._refresh_run_payload(run_payload, run_json, include=include or [])
        process_id = run_payload.get("process_id")
        rendered = _render_run_payload(run_payload, detail=detail)
        if include and isinstance(process_id, str) and process_id:
            for section in ("progress", "artifact_summary", "diagnosis", "next_actions"):
                if section in run_payload:
                    rendered[section] = run_payload[section]
            rendered["includes"] = list(dict.fromkeys(include))
        return rendered

    def read_run_logs(
        self,
        run_id: str,
        *,
        stream: str = "nextflow",
        view: Literal["important", "raw"] = "important",
        after_line: int | None = None,
        start_line: int | None = None,
        end_line: int | None = None,
        tail: int | None = 50,
    ) -> dict[str, Any]:
        """Read one run log stream by delegating to the underlying process."""
        run_payload, _run_json = self._load_run(run_id)
        process_id = _require_run_process_id(run_payload, run_id)
        payload = self._process_manager.read_logs(
            process_id,
            stream=stream,
            view=view,
            after_line=after_line,
            start_line=start_line,
            end_line=end_line,
            tail=tail,
        )
        payload["run_id"] = run_id
        payload.pop("process_id", None)
        return payload

    def get_run_artifacts(
        self,
        run_id: str,
        *,
        section: str,
        root_label: str | None = None,
        path_contains: str | None = None,
        detail: str = "auto",
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Read one run artifact section by delegating to the underlying process."""
        run_payload, _run_json = self._load_run(run_id)
        process_id = _require_run_process_id(run_payload, run_id)
        payload = self._process_manager.get_process_artifacts(
            process_id,
            section=section,
            root_label=root_label,
            path_contains=path_contains,
            detail=detail,
            limit=limit,
            offset=offset,
        )
        payload["run_id"] = run_id
        payload.pop("process_id", None)
        return payload

    def stop_run(self, run_id: str, *, force: bool = False) -> dict[str, Any]:
        """Stop one active run."""
        run_payload, run_json = self._load_run(run_id)
        process_id = _require_run_process_id(run_payload, run_id)
        stop_payload = self._process_manager.stop_process(process_id, force=force)
        merged = self._merge_process_payload(run_payload, stop_payload)
        write_json(run_json, merged)
        return {
            "run_id": run_id,
            "requested": bool(stop_payload.get("requested", False)),
            "run": _render_run_payload(merged, detail="summary"),
        }

    def delete_run(self, run_id: str) -> dict[str, Any]:
        """Delete one prepared or terminal run and its project-owned directories."""
        run_payload, run_json = self._load_run(run_id)
        process_id = run_payload.get("process_id")
        if isinstance(process_id, str) and process_id:
            self._process_manager.delete_process(process_id)

        run_root = Path(str(run_payload["run_root"]))
        results_dir = Path(str(run_payload["results_dir"]))
        if run_root.exists():
            shutil.rmtree(run_root)
        if results_dir.exists():
            shutil.rmtree(results_dir)
        if run_json.exists():
            run_json.unlink()

        return {
            "run_id": run_id,
            "deleted": True,
            "run_root": str(run_root),
            "results_dir": str(results_dir),
        }

    def _ensure_project(self, project_paths: "_ProjectPaths") -> bool:
        """Create one project directory tree and project.json if needed."""
        created = not project_paths.project_root.exists()
        project_paths.project_root.mkdir(parents=True, exist_ok=True)
        (project_paths.project_root / "runs").mkdir(parents=True, exist_ok=True)
        (project_paths.project_root / "results").mkdir(parents=True, exist_ok=True)

        project_payload = read_json(project_paths.project_json)
        timestamp = _utcnow()
        if project_payload is None:
            project_payload = {
                "project_id": project_paths.project_id,
                "project_root": str(project_paths.project_root),
                "created_at": timestamp,
                "updated_at": timestamp,
            }
        else:
            project_payload["updated_at"] = timestamp
        write_json(project_paths.project_json, project_payload)
        return created

    def _list_runs(
        self,
        *,
        project: str | None = None,
        pipeline: str | None = None,
        status: str | None = None,
        run_name_contains: str | None = None,
        artifact_path_contains: str | None = None,
        finished_after: str | None = None,
        finished_before: str | None = None,
        detail: Literal["summary", "full"] = "summary",
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Internal run-list implementation shared by project_get and run_list."""
        if limit < 0:
            raise ValueError("limit must be >= 0")
        if offset < 0:
            raise ValueError("offset must be >= 0")

        matched_process_ids: set[str] | None = None
        if artifact_path_contains is not None:
            matched_process_ids = set(
                self._store.find_process_ids_by_artifact_path_contains(artifact_path_contains)
            )

        runs: list[dict[str, Any]] = []
        for run_json in sorted(self._projects_root.glob("*/runs/*/run.json"), reverse=True):
            payload = read_json(run_json)
            if payload is None:
                continue

            process_id = payload.get("process_id")
            if matched_process_ids is not None and (
                not isinstance(process_id, str) or process_id not in matched_process_ids
            ):
                continue
            if project is not None and payload.get("project_id") != project:
                continue

            payload = self._refresh_run_payload(payload, run_json)

            if pipeline is not None and pipeline not in {
                payload.get("pipeline"),
                payload.get("pipeline_public"),
            }:
                continue
            if status is not None and payload.get("status") != status:
                continue
            if run_name_contains is not None and run_name_contains not in str(
                payload.get("run_name")
            ):
                continue
            if not _matches_finished_window(
                payload,
                finished_after=finished_after,
                finished_before=finished_before,
            ):
                continue
            runs.append(payload)

        sliced = runs[offset : offset + limit]
        return {
            "detail": detail,
            "count": len(sliced),
            "total": len(runs),
            "runs": [_render_run_payload(item, detail=detail) for item in sliced],
        }

    def _load_projects(self) -> list[dict[str, Any]]:
        """Load all project.json files under the configured projects root."""
        projects: list[dict[str, Any]] = []
        for project_json in sorted(self._projects_root.glob("*/project.json"), reverse=True):
            payload = read_json(project_json)
            if payload is not None:
                projects.append(payload)
        return projects

    def _load_run(self, run_id: str) -> tuple[dict[str, Any], Path]:
        """Load one run.json by scanning the projects root."""
        resolved_run_id = _validate_identifier(run_id, field_name="run_id")
        for run_json in self._projects_root.glob(f"*/runs/{resolved_run_id}/run.json"):
            payload = read_json(run_json)
            if payload is not None:
                return payload, run_json
        raise ResourceNotFoundError(
            resource_type="run",
            resource_id=resolved_run_id,
            message=f"Unknown run: {resolved_run_id}",
        )

    def _refresh_run_payload(
        self,
        run_payload: dict[str, Any],
        run_json: Path,
        *,
        include: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """Refresh one run payload from the current underlying process state."""
        refreshed = dict(run_payload)
        process_id = refreshed.get("process_id")
        if isinstance(process_id, str) and process_id:
            process_payload = self._process_manager.get_process(
                process_id,
                include=include or [],
                detail="full",
            )
            refreshed = self._merge_process_payload(refreshed, process_payload)

        refreshed = self._enrich_run_payload(refreshed)
        write_json(run_json, refreshed)
        return refreshed

    def _enrich_run_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Add derived launch and resume metadata to one run payload."""
        enriched = dict(payload)
        enriched["launch_spec"] = _build_launch_spec(enriched)
        enriched.update(_build_resume_metadata(enriched))
        return enriched

    def _build_run_payload(
        self,
        *,
        project_id: str,
        project_root: Path,
        run_id: str,
        run_name: str | None,
        process_id: str | None,
        process_record: dict[str, Any] | None,
        prepared: Any,
    ) -> dict[str, Any]:
        """Build one persisted run.json payload."""
        run_layout = dict(prepared.command_extra["run_layout"])
        payload: dict[str, Any] = {
            "project_id": project_id,
            "project_root": str(project_root),
            "run_id": run_id,
            "run_name": run_name,
            "process_id": process_id,
            "kind": "nextflow",
            "pipeline": prepared.command_extra["pipeline"],
            "pipeline_public": prepared.command_extra["pipeline_public"],
            "entry": prepared.command_extra["entry"],
            "profile": prepared.command_extra["profile"],
            "status": "prepared" if process_record is None else str(process_record["status"]),
            "exit_code": None if process_record is None else process_record.get("exit_code"),
            "timed_out": (
                False if process_record is None else bool(process_record.get("timed_out", False))
            ),
            "stop_requested": (
                False
                if process_record is None
                else bool(process_record.get("stop_requested", False))
            ),
            "created_at": (
                _utcnow() if process_record is None else str(process_record["created_at"])
            ),
            "updated_at": (
                _utcnow() if process_record is None else str(process_record["updated_at"])
            ),
            "started_at": None if process_record is None else process_record.get("started_at"),
            "finished_at": None if process_record is None else process_record.get("finished_at"),
            "run_root": run_layout["run_root"],
            "results_dir": run_layout["results_dir"],
            "work_dir": run_layout["work_dir"],
            "job_dir": run_layout["job_dir"],
            "config_files": list(prepared.command_extra["config_files"]),
            "params": dict(prepared.command_extra["params"]),
            "resume": bool(prepared.command_extra["resume"]),
            "resume_session_id": prepared.command_extra["resume_session_id"],
            "extra_args": list(prepared.command_extra["extra_args"]),
            "resume_source_run_id": prepared.command_extra.get("resume_source_run_id"),
            "archived_job_dir": prepared.command_extra.get("archived_job_dir"),
            "run_layout": run_layout,
            "layout_warnings": list(prepared.command_extra["layout_warnings"]),
        }
        if process_record is not None:
            payload["nextflow_log"] = process_record.get("nextflow_log")
            payload["pipeline_fingerprint"] = process_record.get("pipeline_fingerprint")
            payload["nextflow_session_uuid"] = process_record.get("nextflow_session_uuid")
        return self._enrich_run_payload(payload)

    def _merge_process_payload(
        self,
        run_payload: dict[str, Any],
        process_payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Merge one full process payload into one run payload."""
        merged = dict(run_payload)
        merged.update(
            {
                "status": process_payload["status"],
                "exit_code": process_payload.get("exit_code"),
                "timed_out": bool(process_payload.get("timed_out", False)),
                "stop_requested": bool(process_payload.get("stop_requested", False)),
                "created_at": process_payload.get("created_at", merged.get("created_at")),
                "updated_at": process_payload.get("updated_at", merged.get("updated_at")),
                "started_at": process_payload.get("started_at"),
                "finished_at": process_payload.get("finished_at"),
                "pipeline": process_payload.get("pipeline", merged.get("pipeline")),
                "pipeline_public": process_payload.get(
                    "pipeline_public",
                    merged.get("pipeline_public"),
                ),
                "entry": process_payload.get("entry", merged.get("entry")),
                "profile": process_payload.get("profile", merged.get("profile")),
                "config_files": process_payload.get("config_files", merged.get("config_files")),
                "params": process_payload.get("params", merged.get("params")),
                "work_dir": process_payload.get("work_dir", merged.get("work_dir")),
                "resume": process_payload.get("resume", merged.get("resume")),
                "resume_session_id": process_payload.get(
                    "resume_session_id",
                    merged.get("resume_session_id"),
                ),
                "extra_args": process_payload.get("extra_args", merged.get("extra_args")),
                "resume_source_run_id": process_payload.get(
                    "resume_source_run_id",
                    merged.get("resume_source_run_id"),
                ),
                "archived_job_dir": process_payload.get(
                    "archived_job_dir",
                    merged.get("archived_job_dir"),
                ),
                "nextflow_log": process_payload.get("nextflow_log"),
                "nextflow_session_uuid": process_payload.get(
                    "nextflow_session_uuid",
                    merged.get("nextflow_session_uuid"),
                ),
                "pipeline_fingerprint": process_payload.get("pipeline_fingerprint"),
                "run_layout": process_payload.get("run_layout", merged.get("run_layout")),
                "layout_warnings": process_payload.get(
                    "layout_warnings",
                    merged.get("layout_warnings"),
                ),
            }
        )
        for section in ("progress", "artifact_summary", "diagnosis", "next_actions"):
            if section in process_payload:
                merged[section] = process_payload[section]
        return self._enrich_run_payload(merged)


class _ProjectPaths:
    """Filesystem paths for one project root."""

    def __init__(self, project_root: Path, project_id: str) -> None:
        self.project_root = project_root
        self.project_id = project_id
        self.project_json = project_root / "project.json"


class _RunPaths:
    """Filesystem paths for one project-owned run root."""

    def __init__(self, run_root: Path, run_id: str, results_dir: Path) -> None:
        self.run_root = run_root
        self.run_id = run_id
        self.run_json = run_root / "run.json"
        self.work_dir = run_root / "work"
        self.generated_configs_dir = run_root / "generated_configs"
        self.job_dir = run_root / "job"
        self.results_dir = results_dir


def _project_paths(projects_root: Path, project_id: str) -> _ProjectPaths:
    """Build one project root path bundle."""
    return _ProjectPaths(project_root=projects_root / project_id, project_id=project_id)


def _run_paths(project_root: Path, run_id: str) -> _RunPaths:
    """Build one run-root path bundle under one project."""
    run_root = project_root / "runs" / run_id
    return _RunPaths(
        run_root=run_root,
        run_id=run_id,
        results_dir=project_root / "results" / run_id,
    )


def _build_launch_spec(payload: dict[str, Any]) -> dict[str, Any]:
    """Build one stable launch-spec view from a stored run payload."""
    return {
        "pipeline": payload.get("pipeline_public", payload.get("pipeline")),
        "entry": payload.get("entry"),
        "profile": payload.get("profile"),
        "config_files": list(payload.get("config_files") or []),
        "params": dict(payload.get("params") or {}),
        "extra_args": list(payload.get("extra_args") or []),
    }


def _build_internal_launch_spec(payload: dict[str, Any]) -> dict[str, Any]:
    """Build an internal launch spec with the real launch target."""
    return {
        "pipeline": payload.get("pipeline"),
        "entry": payload.get("entry"),
        "profile": payload.get("profile"),
        "config_files": list(payload.get("config_files") or []),
        "params": dict(payload.get("params") or {}),
        "extra_args": list(payload.get("extra_args") or []),
    }


def _build_resume_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    """Build one compact resume-compatibility summary for a stored run."""
    nextflow_session_uuid = payload.get("nextflow_session_uuid")
    run_root = Path(str(payload["run_root"])) if payload.get("run_root") else None
    work_dir_value = payload.get("work_dir")
    work_dir = (
        Path(str(work_dir_value)) if isinstance(work_dir_value, str) and work_dir_value else None
    )

    resume_compatible = (
        payload.get("kind") == "nextflow"
        and payload.get("status") not in {"prepared", "running"}
        and isinstance(nextflow_session_uuid, str)
        and bool(nextflow_session_uuid)
        and run_root is not None
        and run_root.exists()
        and work_dir is not None
        and work_dir.exists()
    )
    resume_incompatible_reason = None
    if payload.get("kind") != "nextflow":
        resume_incompatible_reason = "Only Nextflow runs expose resume metadata."
    elif payload.get("status") == "prepared":
        resume_incompatible_reason = "The run has not started yet, so no Nextflow session exists."
    elif payload.get("status") == "running":
        resume_incompatible_reason = (
            "Wait for the current run to stop before reusing it as a source."
        )
    elif not isinstance(nextflow_session_uuid, str) or not nextflow_session_uuid:
        resume_incompatible_reason = "Could not read a Nextflow session UUID from nextflow.log."
    elif run_root is None or not run_root.exists():
        resume_incompatible_reason = "The original run root no longer exists on the server."
    elif work_dir is None or not work_dir.exists():
        resume_incompatible_reason = "The original work directory no longer exists on the server."

    return {
        "nextflow_session_uuid": nextflow_session_uuid,
        "resume_compatible": resume_compatible,
        "resume_requires_same_run_root": payload.get("kind") == "nextflow",
        "resume_requires_same_work_dir": payload.get("kind") == "nextflow",
        "resume_incompatible_reason": resume_incompatible_reason,
    }


def _archive_existing_job_dir(job_dir: Path) -> str:
    """Move one previous run job directory aside before reusing the run_id."""
    archive_name = f"{job_dir.name}.previous.{_utcnow().replace(':', '').replace('-', '')}"
    archive_path = job_dir.with_name(archive_name)
    counter = 1
    while archive_path.exists():
        archive_path = job_dir.with_name(f"{archive_name}.{counter}")
        counter += 1
    job_dir.rename(archive_path)
    return str(archive_path)


def _load_project(project_json: Path) -> dict[str, Any] | None:
    """Read one project.json payload if it exists."""
    return read_json(project_json)


def _render_project_payload(payload: dict[str, Any], *, detail: str) -> dict[str, Any]:
    """Render one project summary or full payload."""
    if detail == "full":
        return dict(payload)
    return {
        "project_id": payload["project_id"],
        "project_root": payload["project_root"],
        "created_at": payload.get("created_at"),
        "updated_at": payload.get("updated_at"),
    }


def _render_run_payload(payload: dict[str, Any], *, detail: str) -> dict[str, Any]:
    """Render one run summary or full payload."""
    if detail == "full":
        rendered = dict(payload)
        rendered["pipeline"] = payload.get("pipeline_public", payload.get("pipeline"))
        return rendered
    return {
        "run_id": payload["run_id"],
        "project_id": payload["project_id"],
        "run_name": payload.get("run_name"),
        "status": payload["status"],
        "exit_code": payload.get("exit_code"),
        "timed_out": bool(payload.get("timed_out", False)),
        "stop_requested": bool(payload.get("stop_requested", False)),
        "created_at": payload.get("created_at"),
        "updated_at": payload.get("updated_at"),
        "started_at": payload.get("started_at"),
        "finished_at": payload.get("finished_at"),
        "pipeline": payload.get("pipeline_public", payload.get("pipeline")),
        "entry": payload.get("entry"),
        "profile": payload.get("profile"),
    }


def _resolve_pipeline_argument(pipeline: str, project_root: Path) -> str:
    """Resolve an explicit relative pipeline path against one project root."""
    pipeline_path = Path(pipeline)
    if pipeline_path.is_absolute():
        return str(pipeline_path.resolve())
    if pipeline.startswith(".") or (project_root / pipeline).exists():
        return str((project_root / pipeline).resolve())
    return pipeline


def _validate_identifier(value: str | None, *, field_name: str) -> str:
    """Validate one project or run identifier."""
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string")
    if not _ID_PATTERN.fullmatch(value):
        raise ValueError(f"{field_name} must match [a-z0-9][a-z0-9-]*")
    return value


def _new_run_id() -> str:
    """Generate one short stable-looking run identifier."""
    return f"run-{uuid.uuid4().hex[:12]}"


def _require_run_process_id(payload: dict[str, Any], run_id: str) -> str:
    """Require one launched process_id for run-scoped delegated actions."""
    process_id = payload.get("process_id")
    if isinstance(process_id, str) and process_id:
        return process_id
    raise ResourceNotFoundError(
        resource_type="process",
        resource_id=run_id,
        message=f"Run {run_id} has not been launched yet",
    )


def _matches_finished_window(
    record: dict[str, Any],
    *,
    finished_after: str | None,
    finished_before: str | None,
) -> bool:
    """Apply a small inclusive finished_at window filter to one record."""
    finished_at = record.get("finished_at")
    if not isinstance(finished_at, str):
        return finished_after is None and finished_before is None
    if finished_after is not None and finished_at < finished_after:
        return False
    if finished_before is not None and finished_at > finished_before:
        return False
    return True
