"""Path resolution and allowlist enforcement."""

from __future__ import annotations

from pathlib import Path

from nextmcp.config import PathsConfig


class PathGuard:
    """Validates paths against configured allowlists."""

    def __init__(self, cfg: PathsConfig) -> None:
        self._read_roots = [Path(r).resolve() for r in cfg.allowed_read_roots]
        self._write_roots = [Path(r).resolve() for r in cfg.allowed_write_roots]

    def resolve(
        self,
        path: str,
        cwd: str | None = None,
        *,
        follow_final_symlink: bool = True,
    ) -> Path:
        """Resolve a path, using cwd for relative paths.

        When ``follow_final_symlink`` is false, the parent directory is
        canonicalized but the final path component is preserved. This is
        safer for write/delete-style operations because callers can inspect
        and reject symlinks instead of transparently operating on targets.
        """
        p = Path(path)
        if not p.is_absolute():
            if cwd is None:
                raise ValueError(f"Relative path '{path}' requires explicit cwd")
            p = Path(cwd) / p
        if follow_final_symlink or p.parent == p:
            return p.resolve()
        return p.parent.resolve() / p.name

    def check_read(self, resolved: Path) -> Path:
        """Ensure resolved path is under an allowed read root."""
        for root in self._read_roots:
            try:
                resolved.relative_to(root)
                return resolved
            except ValueError:
                continue
        raise PermissionError(f"Read denied: {resolved} is not under any allowed read root")

    def check_write(self, resolved: Path) -> Path:
        """Ensure resolved path is under an allowed write root."""
        for root in self._write_roots:
            try:
                resolved.relative_to(root)
                return resolved
            except ValueError:
                continue
        raise PermissionError(f"Write denied: {resolved} is not under any allowed write root")

    def resolve_read(self, path: str, cwd: str | None = None) -> Path:
        """Resolve and validate a path for reading."""
        return self.check_read(self.resolve(path, cwd))

    def resolve_write(self, path: str, cwd: str | None = None) -> Path:
        """Resolve and validate a path for writing.

        The final path component is preserved so write-side callers can
        explicitly reject symlinks before mutating the filesystem.
        """
        return self.check_write(self.resolve(path, cwd, follow_final_symlink=False))
