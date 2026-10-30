"""Local Nextflow pipeline catalog helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from nextmcp.errors import ResourceNotFoundError
from nextmcp.nextflow_schema import flatten_nextflow_schema
from nextmcp.paths import PathGuard


@dataclass(frozen=True)
class LocalPipeline:
    """Metadata for one local Nextflow pipeline directory."""

    pipeline_id: str
    pipeline_dir: Path
    main_script: Path
    source_root: Path | None
    nextflow_config: Path | None
    schema_path: Path | None
    readme_path: Path | None
    docs: tuple[Path, ...]
    entry_scripts: tuple[Path, ...]
    workflow_scripts: tuple[Path, ...]
    schema_title: str | None
    schema_description: str | None

    def to_summary_dict(self, *, include_materials: bool = True) -> dict[str, Any]:
        """Serialize compact metadata for pipeline listing."""
        if not include_materials:
            return {
                "pipeline_id": self.pipeline_id,
            }
        return {
            "pipeline_id": self.pipeline_id,
            "pipeline_dir": str(self.pipeline_dir),
            "schema_title": self.schema_title,
            "schema_description": self.schema_description,
        }

    def to_detail_dict(self) -> dict[str, Any]:
        """Serialize detailed metadata for one pipeline."""
        return {
            "pipeline_id": self.pipeline_id,
            "pipeline_dir": str(self.pipeline_dir),
            "source_root": str(self.source_root) if self.source_root is not None else None,
        }


class NextflowPipelineCatalog:
    """Discover and resolve local Nextflow pipelines from configured roots."""

    def __init__(self, pipeline_roots: list[str], guard: PathGuard | None = None) -> None:
        self._pipeline_roots = [Path(root).resolve() for root in pipeline_roots]
        self._guard = guard

    def resolve_path(self, path: str, cwd: str | None = None) -> Path:
        """Resolve a path under pipeline roots or generic read roots."""
        resolved = _resolve_server_path(path, cwd)
        if self._is_under_pipeline_roots(resolved):
            return resolved
        if self._guard is not None:
            try:
                return self._guard.check_read(resolved)
            except PermissionError as exc:
                raise PermissionError(
                    f"Read denied: {resolved} is not under any allowed read root or pipeline root"
                ) from exc
        raise PermissionError(f"Read denied: {resolved} is not under any configured pipeline root")

    def list_pipelines(self) -> list[LocalPipeline]:
        """Return all pipelines discovered under configured roots."""
        pipelines: list[LocalPipeline] = []
        for root in self._resolved_roots():
            for child in sorted(root.iterdir()):
                if child.name.startswith(".") or not child.is_dir():
                    continue
                main_script = child / "main.nf"
                if not main_script.is_file():
                    continue
                pipelines.append(self._build_pipeline(child, source_root=root))
        return pipelines

    def resolve_pipeline(self, pipeline: str, cwd: str | None = None) -> LocalPipeline:
        """Resolve a pipeline by explicit path or configured local pipeline ID."""
        if not pipeline:
            raise ValueError("pipeline must be a non-empty string")

        pipeline_path = Path(pipeline)
        if pipeline_path.is_absolute():
            return self._build_pipeline_from_path(self.resolve_path(pipeline))

        if pipeline.startswith("."):
            return self._build_pipeline_from_path(self.resolve_path(pipeline, cwd))

        if cwd is not None and (Path(cwd) / pipeline).exists():
            return self._build_pipeline_from_path(self.resolve_path(pipeline, cwd))

        matches = [item for item in self.list_pipelines() if item.pipeline_id == pipeline]
        if not matches:
            raise ResourceNotFoundError(
                resource_type="pipeline",
                resource_id=pipeline,
                message=f"Unknown local pipeline: {pipeline}",
            )
        if len(matches) > 1:
            raise ValueError(
                f"Ambiguous local pipeline '{pipeline}' found in multiple pipeline_roots"
            )
        return matches[0]

    def inspect_pipeline(
        self,
        pipeline: str,
        cwd: str | None = None,
        *,
        detail: Literal["summary", "materials"] = "summary",
    ) -> dict[str, Any]:
        """Read one pipeline's metadata plus optional inlined source materials."""
        record = self.resolve_pipeline(pipeline, cwd)
        return build_pipeline_inspect_payload(record, detail=detail)

    def _resolved_roots(self) -> list[Path]:
        """Resolve configured pipeline roots."""
        if not self._pipeline_roots:
            raise ValueError("nextflow.pipeline_roots is empty")

        roots: list[Path] = []
        for root in self._pipeline_roots:
            if not root.is_dir():
                raise FileNotFoundError(f"Configured pipeline root is not a directory: {root}")
            roots.append(root)
        return roots

    def _is_under_pipeline_roots(self, path: Path) -> bool:
        """Return whether one resolved path stays under a configured pipeline root."""
        for root in self._pipeline_roots:
            try:
                path.relative_to(root)
                return True
            except ValueError:
                continue
        return False

    def _build_pipeline_from_path(self, resolved_path: Path) -> LocalPipeline:
        """Load pipeline metadata from an explicit filesystem path."""
        return load_local_pipeline(resolved_path, source_root=self._matching_root(resolved_path))

    def _matching_root(self, pipeline_dir: Path) -> Path | None:
        """Return the configured root containing this pipeline, if any."""
        if not self._pipeline_roots:
            return None
        for root in self._resolved_roots():
            try:
                pipeline_dir.relative_to(root)
                return root
            except ValueError:
                continue
        return None

    def _build_pipeline(self, pipeline_dir: Path, *, source_root: Path | None) -> LocalPipeline:
        """Construct pipeline metadata from a directory."""
        return load_local_pipeline(pipeline_dir, source_root=source_root)


def load_local_pipeline(
    resolved_path: Path,
    *,
    source_root: Path | None = None,
) -> LocalPipeline:
    """Load one local pipeline from a resolved directory or main.nf path."""
    if resolved_path.is_file():
        if resolved_path.name != "main.nf":
            raise FileNotFoundError(f"Expected pipeline main.nf, got: {resolved_path}")
        pipeline_dir = resolved_path.parent
    else:
        pipeline_dir = resolved_path

    main_script = pipeline_dir / "main.nf"
    if not main_script.is_file():
        raise FileNotFoundError(f"Pipeline directory is missing main.nf: {pipeline_dir}")

    schema_path = _optional_file(pipeline_dir / "nextflow_schema.json")
    readme_path = _optional_file(pipeline_dir / "README.md")
    docs = _collect_docs(pipeline_dir, readme_path)
    schema_summary = _read_schema_summary(schema_path)

    return LocalPipeline(
        pipeline_id=pipeline_dir.name,
        pipeline_dir=pipeline_dir,
        main_script=main_script,
        source_root=source_root,
        nextflow_config=_optional_file(pipeline_dir / "nextflow.config"),
        schema_path=schema_path,
        readme_path=readme_path,
        docs=docs,
        entry_scripts=_collect_entry_scripts(pipeline_dir),
        workflow_scripts=_collect_workflow_scripts(pipeline_dir),
        schema_title=schema_summary.get("title"),
        schema_description=schema_summary.get("description"),
    )


def _resolve_server_path(path: str, cwd: str | None = None) -> Path:
    """Resolve one server-side path against an optional cwd."""
    candidate = Path(path)
    if not candidate.is_absolute():
        if cwd is None:
            raise ValueError(f"Relative path '{path}' requires explicit cwd")
        candidate = Path(cwd) / candidate
    return candidate.resolve()


def _optional_file(path: Path) -> Path | None:
    """Return the path if it exists as a file."""
    return path if path.is_file() else None


def _collect_docs(pipeline_dir: Path, readme_path: Path | None) -> tuple[Path, ...]:
    """Collect docs/*.md files."""
    docs: list[Path] = []
    docs_dir = pipeline_dir / "docs"
    if docs_dir.is_dir():
        docs.extend(
            sorted(
                path
                for path in docs_dir.iterdir()
                if path.is_file() and path.suffix.lower() in {".md", ".markdown"}
            )
        )

    return tuple(docs)


def _collect_entry_scripts(pipeline_dir: Path) -> tuple[Path, ...]:
    """Collect top-level alternate .nf entry scripts."""
    return tuple(
        sorted(
            path for path in pipeline_dir.glob("*.nf") if path.is_file() and path.name != "main.nf"
        )
    )


def _collect_workflow_scripts(pipeline_dir: Path) -> tuple[Path, ...]:
    """Collect workflow scripts under workflows/."""
    workflows_dir = pipeline_dir / "workflows"
    if not workflows_dir.is_dir():
        return ()
    return tuple(sorted(path for path in workflows_dir.glob("*.nf") if path.is_file()))


def _read_schema_summary(schema_path: Path | None) -> dict[str, str | None]:
    """Read title/description from nextflow_schema.json when present."""
    payload = read_schema_payload(schema_path)
    if payload is None:
        return {"title": None, "description": None}
    return {
        "title": str(payload.get("title")) if payload.get("title") is not None else None,
        "description": (
            str(payload.get("description")) if payload.get("description") is not None else None
        ),
    }


def read_schema_payload(schema_path: Path | None) -> dict[str, Any] | None:
    """Read the parsed nextflow_schema.json payload when present."""
    if schema_path is None:
        return None

    payload = json.loads(schema_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {schema_path}")
    return payload


def build_pipeline_inspect_payload(
    record: LocalPipeline,
    *,
    detail: Literal["summary", "materials"] = "summary",
) -> dict[str, Any]:
    """Build one inspect-style payload from a local pipeline record."""
    schema = read_schema_payload(record.schema_path)
    payload = {
        **record.to_detail_dict(),
        "detail": detail,
        "schema_summary": _build_schema_summary(record, schema),
    }
    if detail == "materials":
        payload["schema"] = schema
        payload["documents"] = _build_documents(record, include_content=True)
        payload["source_files"] = _build_source_files(record, include_content=True)
        return payload

    payload["documents"] = _build_documents(record, include_content=False)
    payload["source_files"] = _build_source_files(record, include_content=False)
    return payload


def _build_schema_summary(
    record: LocalPipeline,
    schema: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build a compact summary of one pipeline schema."""
    summary: dict[str, Any] = {
        "available": schema is not None,
        "path": str(record.schema_path) if record.schema_path is not None else None,
        "title": record.schema_title,
        "description": record.schema_description,
        "param_count": 0,
        "required_params": [],
        "parameter_names": [],
        "default_params": {},
    }
    if schema is None:
        return summary

    flattened = flatten_nextflow_schema(schema)
    default_params = {
        name: field_schema["default"]
        for name, field_schema in flattened.properties.items()
        if "default" in field_schema
    }
    summary["param_count"] = len(flattened.properties)
    summary["required_params"] = sorted(flattened.required)
    summary["parameter_names"] = sorted(flattened.properties)
    summary["default_params"] = default_params
    return summary


def _build_documents(
    record: LocalPipeline,
    *,
    include_content: bool,
) -> list[dict[str, str]]:
    """Build readme/docs materials for one pipeline."""
    documents: list[dict[str, str]] = []
    if record.readme_path is not None:
        documents.append(
            _asset_descriptor(
                record.readme_path,
                role="readme",
                include_content=include_content,
            )
        )
    documents.extend(
        _asset_descriptor(path, role="doc", include_content=include_content) for path in record.docs
    )
    return documents


def _build_source_files(
    record: LocalPipeline,
    *,
    include_content: bool,
) -> list[dict[str, str]]:
    """Build source-file materials for one pipeline."""
    source_files = [
        _asset_descriptor(
            record.main_script,
            role="main_script",
            include_content=include_content,
        )
    ]
    if record.nextflow_config is not None:
        source_files.append(
            _asset_descriptor(
                record.nextflow_config,
                role="nextflow_config",
                include_content=include_content,
            )
        )
    source_files.extend(
        _asset_descriptor(path, role="entry_script", include_content=include_content)
        for path in record.entry_scripts
    )
    source_files.extend(
        _asset_descriptor(path, role="workflow_script", include_content=include_content)
        for path in record.workflow_scripts
    )
    return source_files


def _asset_descriptor(path: Path, role: str, include_content: bool) -> dict[str, str]:
    """Build one asset descriptor, with optional text content."""
    payload = {
        "role": role,
        "path": str(path),
    }
    if include_content:
        payload["content"] = path.read_text(encoding="utf-8", errors="replace")
    return payload
