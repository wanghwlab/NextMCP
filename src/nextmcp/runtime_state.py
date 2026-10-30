"""Shared runtime state with optional config hot reload."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path

from nextmcp.audit import configure_audit_logger
from nextmcp.config import AppConfig, load_config, validate_config
from nextmcp.nextflow_catalog import NextflowPipelineCatalog
from nextmcp.paths import PathGuard
from nextmcp.process_runtime import ProcessManager
from nextmcp.process_store import ProcessStore
from nextmcp.project_run_manager import ProjectRunManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RuntimeSnapshot:
    """Current config plus derived runtime helpers."""

    cfg: AppConfig
    guard: PathGuard
    store: ProcessStore
    process_manager: ProcessManager
    project_run_manager: ProjectRunManager
    nextflow_catalog: NextflowPipelineCatalog | None


class RuntimeState:
    """Own current config/runtime objects and reload them when config changes."""

    def __init__(self, cfg: AppConfig, config_path: str | Path | None = None) -> None:
        self._config_path = Path(config_path).resolve() if config_path is not None else None
        self._last_checked_at = 0.0
        self._last_mtime_ns = self._read_mtime_ns()
        self._snapshot = self._build_snapshot(cfg)

    @property
    def config_path(self) -> Path | None:
        """Return the tracked config file path, if any."""
        return self._config_path

    @property
    def cfg(self) -> AppConfig:
        """Expose the current config."""
        return self._snapshot.cfg

    def snapshot(self) -> RuntimeSnapshot:
        """Return the current runtime snapshot."""
        return self._snapshot

    def maybe_reload(self) -> bool:
        """Reload config from disk when hot reload is enabled and the file changed."""
        if self._config_path is None or not self._snapshot.cfg.server.reload_config_on_change:
            return False

        interval_seconds = self._snapshot.cfg.server.reload_config_interval_seconds
        interval_seconds = max(interval_seconds, 0.0)
        now = time.monotonic()
        if now - self._last_checked_at < interval_seconds:
            return False
        self._last_checked_at = now

        current_mtime_ns = self._read_mtime_ns()
        if current_mtime_ns is None or current_mtime_ns == self._last_mtime_ns:
            return False

        try:
            self.reload(load_config(self._config_path))
        except Exception:
            self._last_mtime_ns = current_mtime_ns
            logger.exception("Failed to reload config from %s", self._config_path)
            return False

        self._last_mtime_ns = current_mtime_ns
        logger.info("Reloaded config from %s", self._config_path)
        return True

    def reload(self, cfg: AppConfig) -> None:
        """Replace the active runtime snapshot with a fresh one."""
        self._snapshot = self._build_snapshot(cfg)
        self._last_mtime_ns = self._read_mtime_ns()

    def _build_snapshot(self, cfg: AppConfig) -> RuntimeSnapshot:
        """Create runtime helpers from config."""
        validate_config(cfg)
        configure_audit_logger(
            file_path=cfg.audit.file_path,
            max_bytes=cfg.audit.max_bytes,
            backup_count=cfg.audit.backup_count,
        )
        guard = PathGuard(cfg.paths)
        store = ProcessStore(cfg.state.db_path)
        process_manager = ProcessManager(cfg, guard, store)
        process_manager.reconcile_all()
        project_run_manager = ProjectRunManager(cfg, guard, store, process_manager)
        nextflow_catalog = (
            NextflowPipelineCatalog(cfg.nextflow.pipeline_roots, guard)
            if cfg.nextflow.pipeline_roots
            else None
        )
        return RuntimeSnapshot(
            cfg=cfg,
            guard=guard,
            store=store,
            process_manager=process_manager,
            project_run_manager=project_run_manager,
            nextflow_catalog=nextflow_catalog,
        )

    def _read_mtime_ns(self) -> int | None:
        """Read mtime_ns for the tracked config file when available."""
        if self._config_path is None or not self._config_path.exists():
            return None
        return self._config_path.stat().st_mtime_ns
