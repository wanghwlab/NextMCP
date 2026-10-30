"""Visibility helpers for server-local pipeline materials."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

PIPELINE_MATERIALS_REDACTION = "<pipeline_materials_redacted>"


def resolve_pipeline_roots(paths: list[str]) -> tuple[Path, ...]:
    """Resolve configured pipeline roots."""
    return tuple(Path(path).resolve() for path in paths)


def is_under_pipeline_roots(path: Path, pipeline_roots: tuple[Path, ...]) -> bool:
    """Return whether a path is inside a configured pipeline root."""
    resolved = path.resolve()
    return any(_is_relative_to(resolved, root) for root in pipeline_roots)


def assert_not_pipeline_material_path(
    path: Path,
    pipeline_roots: tuple[Path, ...],
    *,
    action: str,
) -> None:
    """Reject direct filesystem access to hidden pipeline material paths."""
    if is_under_pipeline_roots(path, pipeline_roots):
        raise PermissionError(
            f"{action} denied: pipeline material paths are hidden by "
            "nextflow.expose_pipeline_materials=false"
        )


def redact_pipeline_materials(value: Any, pipeline_roots: tuple[Path, ...]) -> Any:
    """Recursively redact configured pipeline-root paths from public payloads."""
    if not pipeline_roots:
        return value
    if isinstance(value, dict):
        return {key: redact_pipeline_materials(item, pipeline_roots) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_pipeline_materials(item, pipeline_roots) for item in value]
    if isinstance(value, tuple):
        return [redact_pipeline_materials(item, pipeline_roots) for item in value]
    if isinstance(value, str):
        return _redact_pipeline_material_string(value, pipeline_roots)
    return value


def _redact_pipeline_material_string(value: str, pipeline_roots: tuple[Path, ...]) -> str:
    value_path = _path_or_none(value)
    if value_path is not None and is_under_pipeline_roots(value_path, pipeline_roots):
        return PIPELINE_MATERIALS_REDACTION

    redacted = value
    for root in sorted(pipeline_roots, key=lambda item: len(str(item)), reverse=True):
        redacted = _redact_embedded_pipeline_path(redacted, root)
    return redacted


def _redact_embedded_pipeline_path(value: str, root: Path) -> str:
    root_text = str(root)
    pattern = re.compile(rf"{re.escape(root_text)}[^\s\"'`,\])}}]*")
    return pattern.sub(PIPELINE_MATERIALS_REDACTION, value)


def _path_or_none(value: str) -> Path | None:
    if "\n" in value or "\r" in value:
        return None
    try:
        return Path(value).expanduser().resolve()
    except OSError:
        return None
    except RuntimeError:
        # expanduser() raises RuntimeError rather than OSError when it cannot
        # resolve a leading "~" because the process has no home directory.
        # Nextflow writes task polling lines such as "~> TaskHandler[...]",
        # and those lines reach this helper as ordinary log strings.
        return None


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True
