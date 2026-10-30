"""Tests for nextmcp.server — BearerAuthMiddleware via create_app."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from nextmcp.config import (
    AppConfig,
    AuthConfig,
    PathsConfig,
    ServerConfig,
    StateConfig,
    load_config,
)
from nextmcp.runtime_state import RuntimeState
from nextmcp.server import create_app, create_mcp

TOKEN = "test-secret-token"


@pytest.fixture
def auth_enabled_app(tmp_path: Path):
    cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=True, bearer_token=TOKEN),
        paths=PathsConfig(
            allowed_read_roots=[str(tmp_path)],
            allowed_write_roots=[str(tmp_path)],
        ),
        state=StateConfig(db_path=str(tmp_path / "state" / "processes.db")),
    )
    runtime = RuntimeState(cfg)
    mcp = create_mcp(cfg)
    return create_app(runtime, mcp)


@pytest.fixture
def auth_disabled_app(tmp_path: Path):
    cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(tmp_path)],
            allowed_write_roots=[str(tmp_path)],
        ),
        state=StateConfig(db_path=str(tmp_path / "state" / "processes.db")),
    )
    runtime = RuntimeState(cfg)
    mcp = create_mcp(cfg)
    return create_app(runtime, mcp)


async def _get(app, headers=None):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get("/", headers=headers)


async def test_auth_disabled_allows_all(auth_disabled_app) -> None:
    resp = await _get(auth_disabled_app)
    assert resp.status_code != 401


async def test_valid_token_passes(auth_enabled_app) -> None:
    resp = await _get(auth_enabled_app, headers={"Authorization": f"Bearer {TOKEN}"})
    assert resp.status_code != 401


async def test_missing_header_rejected(auth_enabled_app) -> None:
    resp = await _get(auth_enabled_app)
    assert resp.status_code == 401
    body = resp.json()
    assert body["ok"] is False
    assert body["error"]["error_code"] == "unauthorized"


async def test_wrong_token_rejected(auth_enabled_app) -> None:
    resp = await _get(auth_enabled_app, headers={"Authorization": "Bearer wrong"})
    assert resp.status_code == 401


async def test_malformed_header_rejected(auth_enabled_app) -> None:
    resp = await _get(auth_enabled_app, headers={"Authorization": "Basic dXNlcjpwYXNz"})
    assert resp.status_code == 401


async def test_request_audit_log_includes_request_id(auth_disabled_app, caplog) -> None:
    caplog.set_level(logging.INFO, logger="nextmcp.audit")

    resp = await _get(auth_disabled_app, headers={"X-Request-Id": "req-123"})

    assert resp.headers["x-request-id"] == "req-123"
    event = _audit_events(caplog)[-1]
    assert event["event"] == "http_request"
    assert event["request_id"] == "req-123"
    assert event["path"] == "/"
    assert event["status_code"] == resp.status_code


async def test_unauthorized_request_is_audited(auth_enabled_app, caplog) -> None:
    caplog.set_level(logging.INFO, logger="nextmcp.audit")

    resp = await _get(auth_enabled_app, headers={"X-Request-Id": "req-401"})

    assert resp.status_code == 401
    assert resp.headers["x-request-id"] == "req-401"
    event = _audit_events(caplog)[-1]
    assert event["event"] == "http_request"
    assert event["request_id"] == "req-401"
    assert event["status_code"] == 401
    assert event["ok"] is False


async def test_auth_token_reload_from_config_file(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        _config_yaml(
            tmp_path,
            auth_enabled=True,
            bearer_token=TOKEN,
            reload_enabled=True,
        )
    )
    runtime = RuntimeState(load_config(config_path), config_path=config_path)
    mcp = create_mcp(runtime.cfg)
    app = create_app(runtime, mcp)

    initial = await _get(app, headers={"Authorization": f"Bearer {TOKEN}"})
    assert initial.status_code != 401

    new_token = "rotated-token"
    config_path.write_text(
        _config_yaml(
            tmp_path,
            auth_enabled=True,
            bearer_token=new_token,
            reload_enabled=True,
        )
    )

    old_token_response = await _get(app, headers={"Authorization": f"Bearer {TOKEN}"})
    assert old_token_response.status_code == 401

    new_token_response = await _get(app, headers={"Authorization": f"Bearer {new_token}"})
    assert new_token_response.status_code != 401


async def test_auth_can_be_enabled_via_hot_reload(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        _config_yaml(
            tmp_path,
            auth_enabled=False,
            bearer_token="",
            reload_enabled=True,
        )
    )
    runtime = RuntimeState(load_config(config_path), config_path=config_path)
    mcp = create_mcp(runtime.cfg)
    app = create_app(runtime, mcp)

    initial = await _get(app)
    assert initial.status_code != 401

    config_path.write_text(
        _config_yaml(
            tmp_path,
            auth_enabled=True,
            bearer_token="later-token",
            reload_enabled=True,
        )
    )

    reloaded = await _get(app)
    assert reloaded.status_code == 401


def _audit_events(caplog: pytest.LogCaptureFixture) -> list[dict[str, object]]:
    return [
        json.loads(record.getMessage())
        for record in caplog.records
        if record.name == "nextmcp.audit"
    ]


def _config_yaml(
    root: Path,
    *,
    auth_enabled: bool,
    bearer_token: str,
    reload_enabled: bool,
) -> str:
    return (
        "server:\n"
        "  reload_config_on_change: "
        f"{'true' if reload_enabled else 'false'}\n"
        "  reload_config_interval_seconds: 0\n"
        "auth:\n"
        f"  enabled: {'true' if auth_enabled else 'false'}\n"
        f'  bearer_token: "{bearer_token}"\n'
        "paths:\n"
        f"  allowed_read_roots:\n    - {root}\n"
        f"  allowed_write_roots:\n    - {root}\n"
        "state:\n"
        f"  db_path: {root / 'state' / 'processes.db'}\n"
    )
