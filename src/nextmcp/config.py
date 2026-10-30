"""Configuration loading and dataclass models."""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]

_REDACTED = "***REDACTED***"
_SENSITIVE_KEY_PARTS = ("token", "secret", "password", "authorization", "api_key", "access_key")


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    base_dir: str = "/data/nextmcp"
    logging_level: str = "INFO"
    reload_config_on_change: bool = False
    reload_config_interval_seconds: float = 1.0


@dataclass
class AuthConfig:
    enabled: bool = True
    bearer_token: str = ""


@dataclass
class PathsConfig:
    allowed_read_roots: list[str] = field(default_factory=lambda: ["/data"])
    allowed_write_roots: list[str] = field(default_factory=lambda: ["/data/nextmcp"])


@dataclass
class StateConfig:
    db_path: str = "/data/nextmcp/state/processes.db"


@dataclass
class ProjectsConfig:
    root: str | None = None


@dataclass
class AuditConfig:
    file_path: str = ""
    max_bytes: int = 5 * 1024 * 1024
    backup_count: int = 3


@dataclass
class NextflowConfig:
    executable: str = "nextflow"
    pipeline_roots: list[str] = field(default_factory=list)
    default_profile: str | None = "docker"
    igenomes_ignore: bool = False
    expose_pipeline_materials: bool = False
    env: dict[str, str] = field(default_factory=dict)


@dataclass
class AppConfig:
    server: ServerConfig = field(default_factory=ServerConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    state: StateConfig = field(default_factory=StateConfig)
    projects: ProjectsConfig = field(default_factory=ProjectsConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)
    nextflow: NextflowConfig = field(default_factory=NextflowConfig)


class ConfigValidationError(ValueError):
    """Raised when application config is internally inconsistent."""


def _merge_dataclass(cls: type, data: dict[str, Any] | None) -> Any:
    """Create a dataclass instance from a dict, ignoring unknown keys."""
    if data is None:
        return cls()
    known = {f.name for f in fields(cls)}
    return cls(**{k: v for k, v in data.items() if k in known})


def load_config(path: str | Path | None = None) -> AppConfig:
    """Load configuration from a YAML file.

    Resolution order:
    1. Explicit path argument
    2. NEXTMCP_CONFIG environment variable
    3. Default: ./config.yaml
    """
    if path is None:
        path = os.environ.get("NEXTMCP_CONFIG", "config.yaml")
    path = Path(path)

    if not path.exists():
        return AppConfig()

    raw: dict[str, Any] = yaml.safe_load(path.read_text()) or {}

    return AppConfig(
        server=_merge_dataclass(ServerConfig, raw.get("server")),
        auth=_merge_dataclass(AuthConfig, raw.get("auth")),
        paths=_merge_dataclass(PathsConfig, raw.get("paths")),
        state=_merge_dataclass(StateConfig, raw.get("state")),
        projects=_merge_dataclass(ProjectsConfig, raw.get("projects")),
        audit=_merge_dataclass(AuditConfig, raw.get("audit")),
        nextflow=_merge_dataclass(NextflowConfig, raw.get("nextflow")),
    )


def validate_config(cfg: AppConfig) -> None:
    """Validate cross-field config constraints."""
    if cfg.server.reload_config_interval_seconds < 0:
        raise ConfigValidationError("server.reload_config_interval_seconds must be >= 0")

    if cfg.auth.enabled and not cfg.auth.bearer_token:
        raise ConfigValidationError("auth.bearer_token must be set when auth.enabled is true")

    if not cfg.paths.allowed_read_roots:
        raise ConfigValidationError("paths.allowed_read_roots must not be empty")

    if not cfg.paths.allowed_write_roots:
        raise ConfigValidationError("paths.allowed_write_roots must not be empty")

    if not cfg.nextflow.executable:
        raise ConfigValidationError("nextflow.executable must not be empty")

    if cfg.nextflow.default_profile is not None and not cfg.nextflow.default_profile:
        raise ConfigValidationError("nextflow.default_profile must not be empty when set")

    if cfg.audit.max_bytes <= 0:
        raise ConfigValidationError("audit.max_bytes must be > 0")

    if cfg.audit.backup_count < 0:
        raise ConfigValidationError("audit.backup_count must be >= 0")

    db_parent = Path(cfg.state.db_path).resolve().parent
    _validate_under_roots(
        db_parent,
        cfg.paths.allowed_write_roots,
        field_name="state.db_path",
        root_field_name="paths.allowed_write_roots",
    )

    _validate_under_roots(
        resolve_projects_root(cfg),
        cfg.paths.allowed_write_roots,
        field_name="projects.root",
        root_field_name="paths.allowed_write_roots",
    )

    if cfg.audit.file_path:
        audit_parent = Path(cfg.audit.file_path).resolve().parent
        _validate_under_roots(
            audit_parent,
            cfg.paths.allowed_write_roots,
            field_name="audit.file_path",
            root_field_name="paths.allowed_write_roots",
        )


def config_to_dict(cfg: AppConfig) -> dict[str, Any]:
    """Convert config dataclasses into a plain dictionary."""
    raw = asdict(cfg)
    if raw["projects"]["root"] is None:
        raw["projects"]["root"] = str(resolve_projects_root(cfg))
    return dict(raw)


def resolve_projects_root(cfg: AppConfig) -> Path:
    """Resolve the effective project root for the active config."""
    if cfg.projects.root:
        return Path(cfg.projects.root).resolve()
    return (Path(cfg.paths.allowed_write_roots[0]).resolve() / "projects").resolve()


def redacted_config_dict(cfg: AppConfig) -> dict[str, Any]:
    """Return a config dictionary with sensitive values redacted."""
    return cast(dict[str, Any], _redact_value(config_to_dict(cfg)))


def _validate_under_roots(
    path: Path,
    roots: list[str],
    *,
    field_name: str,
    root_field_name: str,
) -> None:
    """Ensure a resolved path stays under at least one configured root."""
    resolved_roots = [Path(root).resolve() for root in roots]
    for root in resolved_roots:
        try:
            path.relative_to(root)
            return
        except ValueError:
            continue
    raise ConfigValidationError(f"{field_name} must stay under {root_field_name}")


def _redact_value(value: Any, *, key: str | None = None) -> Any:
    """Recursively redact sensitive config values."""
    if key is not None and any(part in key.lower() for part in _SENSITIVE_KEY_PARTS):
        return _REDACTED

    if isinstance(value, dict):
        return {
            item_key: _redact_value(item_value, key=str(item_key))
            for item_key, item_value in value.items()
        }

    if isinstance(value, list):
        return [_redact_value(item) for item in value]

    return value
