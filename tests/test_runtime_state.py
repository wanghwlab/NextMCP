"""Tests for runtime hot reload state management."""

from __future__ import annotations

from pathlib import Path

import pytest

from nextmcp.config import (
    AppConfig,
    AuthConfig,
    PathsConfig,
    ServerConfig,
    StateConfig,
    load_config,
)
from nextmcp.paths import PathGuard
from nextmcp.process_runtime import ProcessManager, get_job_paths
from nextmcp.process_store import ProcessStore
from nextmcp.runtime_state import RuntimeState


def test_maybe_reload_updates_paths_and_state_locations(tmp_path: Path) -> None:
    root_a = tmp_path / "root-a"
    root_b = tmp_path / "root-b"
    root_a.mkdir()
    root_b.mkdir()

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        _config_yaml(
            read_root=root_a,
            write_root=root_a,
            db_path=root_a / "state-a" / "processes.db",
            reload_enabled=True,
        )
    )

    runtime = RuntimeState(load_config(config_path), config_path=config_path)
    snapshot = runtime.snapshot()
    assert snapshot.guard.resolve_write(str(root_a / "ok.txt")) == root_a / "ok.txt"

    config_path.write_text(
        _config_yaml(
            read_root=root_b,
            write_root=root_b,
            db_path=root_b / "state-b" / "processes.db",
            reload_enabled=True,
        )
    )

    assert runtime.maybe_reload() is True

    reloaded = runtime.snapshot()
    assert reloaded.cfg.state.db_path == str(root_b / "state-b" / "processes.db")
    assert reloaded.guard.resolve_write(str(root_b / "ok.txt")) == root_b / "ok.txt"
    assert reloaded.cfg.projects.root is None
    assert reloaded.project_run_manager is not None


def test_maybe_reload_keeps_previous_snapshot_on_invalid_yaml(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        _config_yaml(
            read_root=root,
            write_root=root,
            db_path=root / "state" / "processes.db",
            reload_enabled=True,
        )
    )

    runtime = RuntimeState(load_config(config_path), config_path=config_path)
    before = runtime.snapshot()

    config_path.write_text("server:\n  reload_config_on_change: [broken\n")

    assert runtime.maybe_reload() is False
    assert runtime.snapshot().cfg == before.cfg


def test_maybe_reload_keeps_previous_snapshot_on_invalid_config(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        _config_yaml(
            read_root=root,
            write_root=root,
            db_path=root / "state" / "processes.db",
            reload_enabled=True,
            auth_enabled=False,
            bearer_token="",
        )
    )

    runtime = RuntimeState(load_config(config_path), config_path=config_path)
    before = runtime.snapshot()

    config_path.write_text(
        _config_yaml(
            read_root=root,
            write_root=root,
            db_path=root / "state" / "processes.db",
            reload_enabled=True,
            auth_enabled=True,
            bearer_token="",
        )
    )

    assert runtime.maybe_reload() is False
    assert runtime.snapshot().cfg == before.cfg


def test_runtime_state_rejects_invalid_initial_config(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        _config_yaml(
            read_root=root,
            write_root=root,
            db_path=root / "state" / "processes.db",
            reload_enabled=False,
            auth_enabled=True,
            bearer_token="",
        )
    )

    with pytest.raises(ValueError, match="auth.bearer_token"):
        RuntimeState(load_config(config_path), config_path=config_path)


def test_reconcile_all_ignores_invalid_process_state_json(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    cfg = AppConfig(
        server=ServerConfig(),
        auth=AuthConfig(enabled=False),
        paths=PathsConfig(
            allowed_read_roots=[str(root)],
            allowed_write_roots=[str(root)],
        ),
        state=StateConfig(db_path=str(root / "state" / "processes.db")),
    )
    store = ProcessStore(cfg.state.db_path)
    manager = ProcessManager(cfg, PathGuard(cfg.paths), store)
    job_dir = root / "state" / "process_jobs" / "proc_bad_state"
    job_paths = get_job_paths(job_dir)
    job_dir.mkdir(parents=True)
    job_paths.result_json.write_text("", encoding="utf-8")
    created_at = "2026-05-07T00:00:00Z"

    store.create_process(
        process_id="proc_bad_state",
        kind="command",
        label=None,
        cwd=str(root),
        argv=["true"],
        job_dir=str(job_dir),
        created_at=created_at,
    )

    manager.reconcile_all()

    record = store.get_process("proc_bad_state")
    assert record is not None
    assert record.status == "failed"
    assert record.finished_at is not None


def _config_yaml(
    *,
    read_root: Path,
    write_root: Path,
    db_path: Path,
    reload_enabled: bool,
    auth_enabled: bool = False,
    bearer_token: str = "",
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
        f"  allowed_read_roots:\n    - {read_root}\n"
        f"  allowed_write_roots:\n    - {write_root}\n"
        "state:\n"
        f"  db_path: {db_path}\n"
    )
