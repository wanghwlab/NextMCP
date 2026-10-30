"""Tests for structured tool responses and audit logging."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

import pytest

from nextmcp.audit import (
    RequestAuditContext,
    configure_audit_logger,
    emit_audit_event,
    reset_request_context,
    set_request_context,
)
from nextmcp.audit import (
    logger as audit_logger,
)
from nextmcp.tool_response import structured_tool


def test_structured_tool_emits_audit_log_with_sanitized_arguments(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="nextmcp.audit")

    @structured_tool
    def fs_write(path: str, content: str) -> dict[str, object]:
        return {"path": path}

    token = set_request_context(
        RequestAuditContext(
            request_id="req-tool",
            method="POST",
            path="/mcp",
            client_ip="127.0.0.1",
            user_agent="pytest",
        )
    )
    try:
        result = fs_write(path="/tmp/result.txt", content="top-secret")
    finally:
        reset_request_context(token)

    assert result["ok"] is True
    event = _tool_events(caplog)[-1]
    assert event["event"] == "tool_call"
    assert event["tool_name"] == "fs_write"
    assert event["request_id"] == "req-tool"
    assert event["arguments"]["kwargs"]["path"] == "/tmp/result.txt"
    assert event["arguments"]["kwargs"]["content"] == {
        "redacted": True,
        "type": "str",
        "length": len("top-secret"),
    }
    assert event["result"]["path"] == "/tmp/result.txt"


def test_structured_tool_logs_mapped_error_code(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="nextmcp.audit")

    @structured_tool
    def run_logs(stream: str) -> dict[str, object]:
        raise ValueError(f"bad stream: {stream}")

    result = run_logs(stream="bad")

    assert result["ok"] is False
    assert result["error"]["error_code"] == "invalid_arguments"
    event = _tool_events(caplog)[-1]
    assert event["event"] == "tool_call"
    assert event["tool_name"] == "run_logs"
    assert event["ok"] is False
    assert event["error_code"] == "invalid_arguments"
    assert event["result"]["error_code"] == "invalid_arguments"


def test_structured_tool_maps_generic_key_error_to_not_found() -> None:
    @structured_tool
    def lookup_record() -> dict[str, object]:
        raise KeyError("Missing generic resource")

    result = lookup_record()

    assert result["ok"] is False
    assert result["error"]["error_code"] == "not_found"
    assert result["error"]["message"] == "Missing generic resource"


@pytest.mark.asyncio
async def test_structured_tool_supports_async_success(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="nextmcp.audit")

    @structured_tool
    async def nextflow_inspect_pipeline(pipeline: str) -> dict[str, object]:
        await asyncio.sleep(0)
        return {"pipeline": pipeline, "has_schema": True}

    token = set_request_context(
        RequestAuditContext(
            request_id="req-async-tool",
            method="POST",
            path="/mcp",
            client_ip="127.0.0.1",
            user_agent="pytest",
        )
    )
    try:
        result = await nextflow_inspect_pipeline(pipeline="rnaseq")
    finally:
        reset_request_context(token)

    assert result["ok"] is True
    assert result["pipeline"] == "rnaseq"
    event = _tool_events(caplog)[-1]
    assert event["event"] == "tool_call"
    assert event["tool_name"] == "nextflow_inspect_pipeline"
    assert event["request_id"] == "req-async-tool"
    assert event["arguments"]["kwargs"]["pipeline"] == "rnaseq"
    assert event["ok"] is True
    assert event["result"]["ok"] is True


@pytest.mark.asyncio
async def test_structured_tool_supports_async_error_mapping(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="nextmcp.audit")

    @structured_tool
    async def fs_read(path: str) -> dict[str, object]:
        await asyncio.sleep(0)
        raise FileNotFoundError(path)

    result = await fs_read(path="/tmp/missing.txt")

    assert result["ok"] is False
    assert result["error"]["error_code"] == "not_found"
    event = _tool_events(caplog)[-1]
    assert event["event"] == "tool_call"
    assert event["tool_name"] == "fs_read"
    assert event["ok"] is False
    assert event["error_code"] == "not_found"
    assert event["result"]["error_code"] == "not_found"


def test_configure_audit_logger_writes_rotating_file(tmp_path: Path) -> None:
    audit_path = tmp_path / "logs" / "audit.log"
    previous_level = audit_logger.level
    audit_logger.setLevel(logging.INFO)
    try:
        configure_audit_logger(
            file_path=str(audit_path),
            max_bytes=4096,
            backup_count=2,
        )
        emit_audit_event({"event": "test_event", "ok": True})
    finally:
        configure_audit_logger(file_path="", max_bytes=4096, backup_count=2)
        audit_logger.setLevel(previous_level)

    lines = audit_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["event"] == "test_event"
    assert payload["ok"] is True


def _tool_events(caplog: pytest.LogCaptureFixture) -> list[dict[str, object]]:
    return [
        json.loads(record.getMessage())
        for record in caplog.records
        if record.name == "nextmcp.audit"
    ]
