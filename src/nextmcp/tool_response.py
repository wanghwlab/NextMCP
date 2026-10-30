"""Structured tool responses for nextmcp."""

from __future__ import annotations

import inspect
import logging
import time
from collections.abc import Awaitable
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar, cast

from nextmcp.audit import log_tool_call
from nextmcp.errors import ResourceNotFoundError

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


@dataclass(frozen=True)
class StructuredToolError(Exception):
    """Tool-facing error with stable metadata for agent recovery."""

    error_code: str
    message: str
    retryable: bool = False
    suggestions: tuple[str, ...] = ()
    details: dict[str, Any] | None = None

    def to_response(self) -> dict[str, Any]:
        """Convert the error to a structured tool payload."""
        error: dict[str, Any] = {
            "error_code": self.error_code,
            "message": self.message,
            "retryable": self.retryable,
            "suggestions": list(self.suggestions),
        }
        if self.details:
            error["details"] = self.details
        return {"ok": False, "error": error}


def structured_tool(
    fn: Callable[P, T] | Callable[P, Awaitable[T]],
) -> Callable[P, dict[str, Any]] | Callable[P, Awaitable[dict[str, Any]]]:
    """Wrap a tool so it always returns a structured dictionary payload."""

    if inspect.iscoroutinefunction(fn):
        async_fn = cast(Callable[P, Awaitable[T]], fn)

        @wraps(fn)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> dict[str, Any]:
            started_at = time.perf_counter()
            try:
                result = await async_fn(*args, **kwargs)
            except Exception as exc:
                response = _response_for_exception(exc, tool_name=fn.__name__)
                return _log_response(
                    tool_name=fn.__name__,
                    args=tuple(args),
                    kwargs=kwargs,
                    response=response,
                    started_at=started_at,
                )

            response = _success_response(result)
            return _log_response(
                tool_name=fn.__name__,
                args=tuple(args),
                kwargs=kwargs,
                response=response,
                started_at=started_at,
            )

        return async_wrapper

    sync_fn = cast(Callable[P, T], fn)

    @wraps(fn)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> dict[str, Any]:
        started_at = time.perf_counter()
        try:
            result = sync_fn(*args, **kwargs)
        except Exception as exc:
            response = _response_for_exception(exc, tool_name=fn.__name__)
            return _log_response(
                tool_name=fn.__name__,
                args=tuple(args),
                kwargs=kwargs,
                response=response,
                started_at=started_at,
            )

        response = _success_response(result)
        return _log_response(
            tool_name=fn.__name__,
            args=tuple(args),
            kwargs=kwargs,
            response=response,
            started_at=started_at,
        )

    return sync_wrapper


def error_payload(
    *,
    error_code: str,
    message: str,
    retryable: bool = False,
    suggestions: list[str] | tuple[str, ...] = (),
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a structured error payload for non-tool HTTP responses."""
    return StructuredToolError(
        error_code=error_code,
        message=message,
        retryable=retryable,
        suggestions=tuple(suggestions),
        details=details,
    ).to_response()


def _success_response(result: object) -> dict[str, Any]:
    """Build the stable success payload for one tool call."""
    if isinstance(result, dict):
        return {"ok": True, **result}
    return {"ok": True, "result": result}


def _response_for_exception(exc: Exception, *, tool_name: str) -> dict[str, Any]:
    """Map one exception to the stable tool-facing error payload."""
    if isinstance(exc, StructuredToolError):
        return exc.to_response()

    mapped = map_exception(exc, tool_name=tool_name)
    if mapped.error_code == "internal_error":
        logger.exception("Unhandled error in tool %s", tool_name)
    return mapped.to_response()


def _log_response(
    *,
    tool_name: str,
    args: tuple[object, ...],
    kwargs: dict[str, object],
    response: dict[str, Any],
    started_at: float,
) -> dict[str, Any]:
    """Emit one audit event for a tool call and return the original response."""
    log_tool_call(
        tool_name=tool_name,
        args=args,
        kwargs=kwargs,
        response=response,
        duration_ms=_duration_ms(started_at),
    )
    return response


def map_exception(exc: Exception, *, tool_name: str) -> StructuredToolError:
    """Map common Python exceptions into stable tool-facing error metadata."""
    message = _message_for_exception(exc)
    details = {
        "tool": tool_name,
        "exception_type": type(exc).__name__,
    }

    if isinstance(exc, PermissionError):
        return StructuredToolError(
            error_code="permission_denied",
            message=message,
            suggestions=(
                (
                    "Check the configured allowed_read_roots, "
                    "allowed_write_roots, and nextflow.pipeline_roots."
                ),
                "Pass an explicit cwd when using a relative path.",
            ),
            details=details,
        )

    if isinstance(exc, FileExistsError):
        return StructuredToolError(
            error_code="already_exists",
            message=message,
            suggestions=(
                "Choose a different destination path.",
                "Pass overwrite=true if replacing the destination is intended.",
            ),
            details=details,
        )

    if isinstance(exc, (IsADirectoryError, NotADirectoryError)):
        return StructuredToolError(
            error_code="invalid_path_type",
            message=message,
            suggestions=(
                "Check whether the target must be a file or a directory.",
                "Use recursive=true when copying or deleting a directory tree.",
            ),
            details=details,
        )

    if isinstance(exc, FileNotFoundError):
        return StructuredToolError(
            error_code="not_found",
            message=message,
            suggestions=(
                "Confirm the target path already exists.",
                "Pass create_parents=true before writing into a new directory tree.",
            ),
            details=details,
        )

    if isinstance(exc, ResourceNotFoundError):
        resource_details = {
            **details,
            "resource_type": exc.resource_type,
            "resource_id": exc.resource_id,
        }
        error_code, suggestions = _resource_not_found_metadata(exc.resource_type)
        return StructuredToolError(
            error_code=error_code,
            message=message,
            suggestions=suggestions,
            details=resource_details,
        )

    if isinstance(exc, KeyError):
        return StructuredToolError(
            error_code="not_found",
            message=message,
            suggestions=(
                "Confirm the referenced resource exists on the server.",
                "Re-run a discovery or list tool before retrying the operation.",
            ),
            details=details,
        )

    if isinstance(exc, ValueError):
        return StructuredToolError(
            error_code="invalid_arguments",
            message=message,
            suggestions=(
                "Review the tool arguments and value types.",
                "Pass cwd explicitly when providing relative paths.",
            ),
            details=details,
        )

    if isinstance(exc, OSError):
        return StructuredToolError(
            error_code="os_error",
            message=message,
            retryable=True,
            suggestions=(
                "Inspect the filesystem or process state on the server.",
                "Retry after fixing the underlying OS-level issue.",
            ),
            details=details,
        )

    return StructuredToolError(
        error_code="internal_error",
        message=message or f"Unexpected error while executing {tool_name}",
        retryable=True,
        suggestions=(
            "Inspect the server logs for a traceback.",
            "Retry after fixing the underlying application issue.",
        ),
        details=details,
    )


def _message_for_exception(exc: Exception) -> str:
    """Extract a stable human-readable message from an exception."""
    if isinstance(exc, KeyError) and exc.args:
        return str(exc.args[0])
    return str(exc) or exc.__class__.__name__


def _resource_not_found_metadata(resource_type: str) -> tuple[str, tuple[str, ...]]:
    """Return the error code and suggestions for one missing resource type."""
    if resource_type == "process":
        return (
            "process_not_found",
            (
                "Use run_list or run_get when you only know the workflow run.",
                'Use the hidden process_id from run_get(detail="full") only '
                "for server-side debugging.",
            ),
        )
    if resource_type == "pipeline":
        return (
            "pipeline_not_found",
            (
                "Call nextflow_list_pipelines to discover valid local pipeline IDs.",
                "Use a configured pipeline ID or an explicit server-local pipeline path.",
            ),
        )
    return (
        "not_found",
        (
            "Confirm the referenced resource exists on the server.",
            "Re-run a discovery or list tool before retrying the operation.",
        ),
    )


def _duration_ms(started_at: float) -> int:
    """Convert a perf-counter start timestamp to whole milliseconds."""
    return max(0, int((time.perf_counter() - started_at) * 1000))
