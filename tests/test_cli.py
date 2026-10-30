"""Tests for the CLI entry point."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nextmcp.cli import main


def test_main_rejects_invalid_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "auth:\n"
        "  enabled: true\n"
        '  bearer_token: ""\n'
        "paths:\n"
        f"  allowed_read_roots:\n    - {tmp_path}\n"
        f"  allowed_write_roots:\n    - {tmp_path}\n"
        "state:\n"
        f"  db_path: {tmp_path / 'state' / 'processes.db'}\n"
    )

    with pytest.raises(SystemExit, match="2"):
        main(["--config", str(config_path)])


def test_main_check_config_exits_without_starting_server(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "auth:\n"
        "  enabled: false\n"
        '  bearer_token: ""\n'
        "paths:\n"
        f"  allowed_read_roots:\n    - {tmp_path}\n"
        f"  allowed_write_roots:\n    - {tmp_path}\n"
        "state:\n"
        f"  db_path: {tmp_path / 'state' / 'processes.db'}\n"
    )

    def _fail_run(*args: object, **kwargs: object) -> None:
        raise AssertionError("uvicorn.run should not be called when --check-config is used")

    monkeypatch.setattr("nextmcp.cli.uvicorn.run", _fail_run)

    main(["--config", str(config_path), "--check-config"])

    captured = capsys.readouterr()
    assert f"Config OK: {config_path}" in captured.out


def test_main_dump_config_redacts_secrets_and_applies_overrides(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "server:\n"
        "  host: 0.0.0.0\n"
        "  port: 8000\n"
        "auth:\n"
        "  enabled: true\n"
        '  bearer_token: "top-secret-token"\n'
        "paths:\n"
        f"  allowed_read_roots:\n    - {tmp_path}\n"
        f"  allowed_write_roots:\n    - {tmp_path}\n"
        "state:\n"
        f"  db_path: {tmp_path / 'state' / 'processes.db'}\n"
        "nextflow:\n"
        "  env:\n"
        '    ACCESS_KEY: "secret-key"\n'
        '    NXF_HOME: "/tmp/nxf"\n'
    )

    def _fail_run(*args: object, **kwargs: object) -> None:
        raise AssertionError("uvicorn.run should not be called when --dump-config is used")

    monkeypatch.setattr("nextmcp.cli.uvicorn.run", _fail_run)

    main(
        [
            "--config",
            str(config_path),
            "--dump-config",
            "--host",
            "127.0.0.1",
            "--port",
            "9000",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["server"]["host"] == "127.0.0.1"
    assert payload["server"]["port"] == 9000
    assert payload["auth"]["bearer_token"] == "***REDACTED***"
    assert payload["nextflow"]["env"]["ACCESS_KEY"] == "***REDACTED***"
    assert payload["nextflow"]["env"]["NXF_HOME"] == "/tmp/nxf"
