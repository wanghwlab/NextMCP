"""Structured audit logging helpers."""

from __future__ import annotations

import contextvars
import json
import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Iterable, Mapping

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

logger = logging.getLogger("nextmcp.audit")
fallback_logger = logging.getLogger(__name__)
_AUDIT_FILE_HANDLER_NAME = "nextmcp_audit_rotating_file"

_request_context: contextvars.ContextVar[RequestAuditContext | None] = contextvars.ContextVar(
    "nextmcp_request_audit_context",
    default=None,
)

_SENSITIVE_KEYS = {"authorization", "bearer_token", "content", "env", "params", "stdin"}
_VERBATIM_STRING_KEYS = {
    "cwd",
    "dst",
    "entry",
    "kind",
    "label",
    "path",
    "pipeline",
    "process_id",
    "profile",
    "src",
    "stream",
    "work_dir",
}
_PREVIEW_SEQUENCE_KEYS = {"argv", "config_files", "extra_args"}
_RESULT_SUMMARY_KEYS = {
    "count",
    "destination",
    "kind",
    "path",
    "process_id",
    "requested",
    "source",
    "status",
    "stream",
    "total",
}


@dataclass(frozen=True)
class RequestAuditContext:
    """Per-request audit metadata propagated to tool calls."""

    request_id: str
    method: str
    path: str
    client_ip: str | None
    user_agent: str | None


class AuditMiddleware(BaseHTTPMiddleware):
    """Attach request context and emit one audit event per HTTP request."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get("x-request-id") or new_request_id()
        context = RequestAuditContext(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )
        request.state.request_id = request_id
        start = time.perf_counter()
        token = _request_context.set(context)

        try:
            response = await call_next(request)
        except Exception as exc:
            log_http_request(
                context=context,
                status_code=500,
                duration_ms=_duration_ms(start),
                error_type=type(exc).__name__,
            )
            raise
        finally:
            _request_context.reset(token)

        response.headers.setdefault("x-request-id", request_id)
        log_http_request(
            context=context,
            status_code=response.status_code,
            duration_ms=_duration_ms(start),
        )
        return response


def get_request_context() -> RequestAuditContext | None:
    """Return the current request audit context, if any."""
    return _request_context.get()


def set_request_context(
    context: RequestAuditContext,
) -> contextvars.Token[RequestAuditContext | None]:
    """Set the current request context and return the reset token."""
    return _request_context.set(context)


def reset_request_context(token: contextvars.Token[RequestAuditContext | None]) -> None:
    """Reset the request context to a previous token."""
    _request_context.reset(token)


def new_request_id() -> str:
    """Create a stable opaque request identifier."""
    return uuid.uuid4().hex


def log_http_request(
    *,
    context: RequestAuditContext,
    status_code: int,
    duration_ms: int,
    error_type: str | None = None,
) -> None:
    """Emit one structured HTTP request audit event."""
    payload: dict[str, Any] = {
        "event": "http_request",
        "request_id": context.request_id,
        "method": context.method,
        "path": context.path,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "ok": status_code < 400,
    }
    if context.client_ip is not None:
        payload["client_ip"] = context.client_ip
    if context.user_agent:
        payload["user_agent"] = context.user_agent
    if error_type is not None:
        payload["error_type"] = error_type
    emit_audit_event(payload)


def log_tool_call(
    *,
    tool_name: str,
    args: tuple[Any, ...],
    kwargs: Mapping[str, Any],
    response: Mapping[str, Any],
    duration_ms: int,
) -> None:
    """Emit one structured tool call audit event."""
    payload: dict[str, Any] = {
        "event": "tool_call",
        "tool_name": tool_name,
        "duration_ms": duration_ms,
        "ok": bool(response.get("ok")),
        "arguments": summarize_arguments(args=args, kwargs=kwargs),
        "result": summarize_result(response),
    }
    error = response.get("error")
    if isinstance(error, Mapping):
        payload["error_code"] = error.get("error_code")

    context = get_request_context()
    if context is not None:
        payload["request_id"] = context.request_id
        payload["request_method"] = context.method
        payload["request_path"] = context.path

    emit_audit_event(payload)


def summarize_arguments(*, args: tuple[Any, ...], kwargs: Mapping[str, Any]) -> dict[str, Any]:
    """Return a JSON-safe summary of tool arguments."""
    summary: dict[str, Any] = {}
    if args:
        summary["args"] = [_summarize_value(None, value) for value in args]
    if kwargs:
        summary["kwargs"] = {
            key: _summarize_value(key, value) for key, value in sorted(kwargs.items())
        }
    return summary


def summarize_result(response: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact JSON-safe result summary for audit logs."""
    summary: dict[str, Any] = {}
    if "ok" in response:
        summary["ok"] = bool(response["ok"])

    for key in _RESULT_SUMMARY_KEYS:
        if key in response:
            summary[key] = _summarize_value(key, response[key])

    result_value = response.get("result")
    if "result" in response and not isinstance(result_value, Mapping):
        summary["result_type"] = type(result_value).__name__

    error = response.get("error")
    if isinstance(error, Mapping):
        error_code = error.get("error_code")
        if isinstance(error_code, str):
            summary["error_code"] = error_code

    return summary


def emit_audit_event(payload: Mapping[str, Any]) -> None:
    """Serialize and emit a JSON audit event without breaking the request path."""
    event = {"ts": utcnow(), **payload}
    try:
        logger.info(json.dumps(event, sort_keys=True, ensure_ascii=True))
    except Exception:
        fallback_logger.exception("Failed to emit audit event %s", payload.get("event"))


def utcnow() -> str:
    """Return an ISO8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def configure_audit_logger(*, file_path: str, max_bytes: int, backup_count: int) -> None:
    """Configure an optional rotating file sink for audit events."""
    _remove_audit_file_handlers()

    if not file_path:
        return

    audit_path = Path(file_path)
    audit_path.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        audit_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.set_name(_AUDIT_FILE_HANDLER_NAME)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)


def _duration_ms(start: float) -> int:
    """Convert a perf-counter start timestamp to whole milliseconds."""
    return max(0, int((time.perf_counter() - start) * 1000))


def _client_ip(request: Request) -> str | None:
    """Prefer X-Forwarded-For when present, otherwise use the direct peer address."""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",", maxsplit=1)[0].strip() or None
    if request.client is None:
        return None
    return request.client.host


def _remove_audit_file_handlers() -> None:
    """Remove previously configured audit file handlers."""
    for handler in list(logger.handlers):
        if handler.get_name() != _AUDIT_FILE_HANDLER_NAME:
            continue
        logger.removeHandler(handler)
        handler.close()


def _summarize_value(key: str | None, value: Any) -> Any:
    """Convert values into bounded JSON-safe summaries."""
    normalized_key = key.lower() if key is not None else None

    if normalized_key in _SENSITIVE_KEYS:
        return _redacted_summary(value)

    if value is None or isinstance(value, bool | int | float):
        return value

    if isinstance(value, Path):
        return _truncate(str(value))

    if isinstance(value, str):
        if normalized_key in _VERBATIM_STRING_KEYS:
            return _truncate(value)
        return {"type": "str", "length": len(value)}

    if isinstance(value, bytes):
        return {"type": "bytes", "length": len(value)}

    if isinstance(value, Mapping):
        keys = sorted(str(item) for item in value.keys())
        return {"type": "dict", "size": len(value), "keys": keys[:10]}

    if isinstance(value, tuple):
        return _summarize_sequence(normalized_key, value, kind="tuple")

    if isinstance(value, list):
        return _summarize_sequence(normalized_key, value, kind="list")

    if isinstance(value, set):
        return _summarize_sequence(normalized_key, sorted(value), kind="set")

    return {"type": type(value).__name__}


def _redacted_summary(value: Any) -> dict[str, Any]:
    """Describe a sensitive value without logging it verbatim."""
    if value is None:
        return {"redacted": True, "type": "none"}
    if isinstance(value, str):
        return {"redacted": True, "type": "str", "length": len(value)}
    if isinstance(value, bytes):
        return {"redacted": True, "type": "bytes", "length": len(value)}
    if isinstance(value, Mapping):
        keys = sorted(str(item) for item in value.keys())
        return {"redacted": True, "type": "dict", "size": len(value), "keys": keys[:10]}
    if isinstance(value, Iterable):
        return {"redacted": True, "type": type(value).__name__}
    return {"redacted": True, "type": type(value).__name__}


def _summarize_sequence(
    key: str | None,
    value: list[Any] | tuple[Any, ...],
    *,
    kind: str,
) -> dict[str, Any]:
    """Describe a bounded sequence for audit logs."""
    summary: dict[str, Any] = {"type": kind, "length": len(value)}
    if key in _PREVIEW_SEQUENCE_KEYS:
        preview = [
            _truncate(item) if isinstance(item, str) else _summarize_value(None, item)
            for item in value[:5]
        ]
        summary["preview"] = preview
    return summary


def _truncate(value: str, limit: int = 200) -> str:
    """Truncate long strings so audit events stay compact."""
    if len(value) <= limit:
        return value
    return f"{value[: limit - 3]}..."
