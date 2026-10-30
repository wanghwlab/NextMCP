"""Tests for nextmcp.config — load_config and _merge_dataclass."""

from __future__ import annotations

from pathlib import Path

import pytest

from nextmcp.config import (
    AppConfig,
    AuditConfig,
    AuthConfig,
    ConfigValidationError,
    NextflowConfig,
    PathsConfig,
    ProjectsConfig,
    ServerConfig,
    StateConfig,
    _merge_dataclass,
    config_to_dict,
    load_config,
    redacted_config_dict,
    validate_config,
)


def test_defaults_when_file_missing(tmp_path: Path) -> None:
    cfg = load_config(tmp_path / "nonexistent.yaml")
    assert cfg.server.port == 8000
    assert cfg.auth.enabled is True
    assert cfg.paths.allowed_read_roots == ["/data"]


def test_empty_yaml(tmp_path: Path) -> None:
    f = tmp_path / "empty.yaml"
    f.write_text("")
    cfg = load_config(f)
    assert cfg.server.port == 8000


def test_partial_yaml(tmp_path: Path) -> None:
    f = tmp_path / "partial.yaml"
    f.write_text("server:\n  port: 9999\n")
    cfg = load_config(f)
    assert cfg.server.port == 9999
    assert cfg.server.host == "0.0.0.0"  # default kept


def test_full_yaml(tmp_path: Path) -> None:
    f = tmp_path / "full.yaml"
    f.write_text(
        "server:\n"
        "  host: 127.0.0.1\n"
        "  port: 3000\n"
        "auth:\n"
        "  enabled: false\n"
        "  bearer_token: tok123\n"
        "paths:\n"
        "  allowed_read_roots:\n"
        "    - /mnt\n"
        "audit:\n"
        "  file_path: /mnt/logs/audit.log\n"
        "  max_bytes: 2048\n"
        "  backup_count: 5\n"
        "nextflow:\n"
        "  executable: /usr/bin/nextflow\n"
        "  pipeline_roots:\n"
        "    - /opt/pipelines\n"
        "  default_profile: singularity\n"
        "  igenomes_ignore: true\n"
        "  expose_pipeline_materials: true\n"
    )
    cfg = load_config(f)
    assert cfg.server.host == "127.0.0.1"
    assert cfg.server.port == 3000
    assert cfg.auth.enabled is False
    assert cfg.auth.bearer_token == "tok123"
    assert cfg.paths.allowed_read_roots == ["/mnt"]
    assert cfg.audit.file_path == "/mnt/logs/audit.log"
    assert cfg.audit.max_bytes == 2048
    assert cfg.audit.backup_count == 5
    assert cfg.nextflow.executable == "/usr/bin/nextflow"
    assert cfg.nextflow.pipeline_roots == ["/opt/pipelines"]
    assert cfg.nextflow.default_profile == "singularity"
    assert cfg.nextflow.igenomes_ignore is True
    assert cfg.nextflow.expose_pipeline_materials is True


def test_validate_config_rejects_empty_nextflow_default_profile(tmp_path: Path) -> None:
    cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(tmp_path)],
            allowed_write_roots=[str(tmp_path)],
        ),
        state=StateConfig(db_path=str(tmp_path / "state" / "processes.db")),
        nextflow=NextflowConfig(default_profile=""),
    )

    with pytest.raises(ConfigValidationError, match="nextflow.default_profile"):
        validate_config(cfg)


def test_unknown_keys_ignored(tmp_path: Path) -> None:
    f = tmp_path / "extra.yaml"
    f.write_text("server:\n  port: 5000\n  unknown_key: hello\n")
    cfg = load_config(f)
    assert cfg.server.port == 5000
    assert not hasattr(cfg.server, "unknown_key")


def test_env_var_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    f = tmp_path / "env.yaml"
    f.write_text("server:\n  port: 7777\n")
    monkeypatch.setenv("NEXTMCP_CONFIG", str(f))
    cfg = load_config()  # no explicit path
    assert cfg.server.port == 7777


def test_explicit_path_wins(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    env_f = tmp_path / "env.yaml"
    env_f.write_text("server:\n  port: 1111\n")
    explicit_f = tmp_path / "explicit.yaml"
    explicit_f.write_text("server:\n  port: 2222\n")
    monkeypatch.setenv("NEXTMCP_CONFIG", str(env_f))
    cfg = load_config(explicit_f)
    assert cfg.server.port == 2222


def test_merge_none() -> None:
    result = _merge_dataclass(ServerConfig, None)
    assert result == ServerConfig()


def test_merge_partial() -> None:
    result = _merge_dataclass(ServerConfig, {"port": 4000})
    assert result.port == 4000
    assert result.host == "0.0.0.0"


def test_merge_extra_keys() -> None:
    result = _merge_dataclass(AuthConfig, {"enabled": False, "bogus": 42})
    assert result.enabled is False
    assert not hasattr(result, "bogus")


def test_validate_config_rejects_enabled_auth_without_token(tmp_path: Path) -> None:
    cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=True, bearer_token=""),
        paths=PathsConfig(
            allowed_read_roots=[str(tmp_path)],
            allowed_write_roots=[str(tmp_path)],
        ),
        state=StateConfig(db_path=str(tmp_path / "state" / "processes.db")),
    )

    with pytest.raises(ConfigValidationError, match="auth.bearer_token"):
        validate_config(cfg)


def test_validate_config_rejects_state_paths_outside_write_roots(tmp_path: Path) -> None:
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    outside_root = tmp_path / "outside"
    outside_root.mkdir()
    cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(tmp_path)],
            allowed_write_roots=[str(allowed_root)],
        ),
        state=StateConfig(db_path=str(outside_root / "state" / "processes.db")),
    )

    with pytest.raises(ConfigValidationError, match="state.db_path"):
        validate_config(cfg)


def test_validate_config_allows_pipeline_roots_outside_read_roots(tmp_path: Path) -> None:
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    outside_root = tmp_path / "outside"
    outside_root.mkdir()
    cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(allowed_root)],
            allowed_write_roots=[str(tmp_path)],
        ),
        state=StateConfig(db_path=str(tmp_path / "state" / "processes.db")),
        nextflow=NextflowConfig(
            executable="nextflow",
            pipeline_roots=[str(outside_root)],
        ),
    )

    validate_config(cfg)


def test_validate_config_rejects_audit_file_outside_write_roots(tmp_path: Path) -> None:
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    outside_root = tmp_path / "outside"
    outside_root.mkdir()
    cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(tmp_path)],
            allowed_write_roots=[str(allowed_root)],
        ),
        state=StateConfig(db_path=str(allowed_root / "state" / "processes.db")),
        audit=AuditConfig(file_path=str(outside_root / "audit.log")),
    )

    with pytest.raises(ConfigValidationError, match="audit.file_path"):
        validate_config(cfg)


def test_redacted_config_dict_hides_sensitive_values(tmp_path: Path) -> None:
    cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=True, bearer_token="secret-token"),
        paths=PathsConfig(
            allowed_read_roots=[str(tmp_path)],
            allowed_write_roots=[str(tmp_path)],
        ),
        state=StateConfig(db_path=str(tmp_path / "state" / "processes.db")),
        nextflow=NextflowConfig(
            env={
                "ACCESS_KEY": "abc123",
                "NXF_HOME": "/tmp/nxf",
            }
        ),
    )

    raw = config_to_dict(cfg)
    redacted = redacted_config_dict(cfg)

    assert raw["auth"]["bearer_token"] == "secret-token"
    assert redacted["auth"]["bearer_token"] == "***REDACTED***"
    assert redacted["nextflow"]["env"]["ACCESS_KEY"] == "***REDACTED***"
    assert redacted["nextflow"]["env"]["NXF_HOME"] == "/tmp/nxf"


def test_config_to_dict_resolves_default_projects_root(tmp_path: Path) -> None:
    cfg = AppConfig(
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(tmp_path)],
            allowed_write_roots=[str(tmp_path)],
        ),
        state=StateConfig(db_path=str(tmp_path / "state" / "processes.db")),
        projects=ProjectsConfig(root=None),
    )

    payload = config_to_dict(cfg)

    assert payload["projects"]["root"] == str((tmp_path / "projects").resolve())


def test_validate_config_rejects_projects_root_outside_write_roots(tmp_path: Path) -> None:
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    outside_root = tmp_path / "outside"
    outside_root.mkdir()
    cfg = AppConfig(
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(tmp_path)],
            allowed_write_roots=[str(allowed_root)],
        ),
        state=StateConfig(db_path=str(allowed_root / "state" / "processes.db")),
        projects=ProjectsConfig(root=str(outside_root / "projects")),
    )

    with pytest.raises(ConfigValidationError, match="projects.root"):
        validate_config(cfg)
