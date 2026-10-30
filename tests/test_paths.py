"""Tests for nextmcp.paths — PathGuard."""

from __future__ import annotations

from pathlib import Path

import pytest

from nextmcp.config import PathsConfig
from nextmcp.paths import PathGuard


@pytest.fixture
def guard_with_roots(tmp_path: Path) -> PathGuard:
    """PathGuard with tmp_path as both read and write root."""
    cfg = PathsConfig(
        allowed_read_roots=[str(tmp_path)],
        allowed_write_roots=[str(tmp_path)],
    )
    return PathGuard(cfg)


def test_resolve_absolute(guard_with_roots: PathGuard, tmp_path: Path) -> None:
    p = guard_with_roots.resolve(str(tmp_path / "foo.txt"))
    assert p == (tmp_path / "foo.txt").resolve()


def test_resolve_relative_with_cwd(guard_with_roots: PathGuard, tmp_path: Path) -> None:
    p = guard_with_roots.resolve("bar.txt", cwd=str(tmp_path))
    assert p == (tmp_path / "bar.txt").resolve()


def test_resolve_relative_no_cwd_raises(guard_with_roots: PathGuard) -> None:
    with pytest.raises(ValueError, match="requires explicit cwd"):
        guard_with_roots.resolve("relative.txt")


def test_check_read_allowed(guard_with_roots: PathGuard, tmp_path: Path) -> None:
    f = tmp_path / "ok.txt"
    result = guard_with_roots.check_read(f.resolve())
    assert result == f.resolve()


def test_check_read_denied(guard_with_roots: PathGuard) -> None:
    with pytest.raises(PermissionError, match="Read denied"):
        guard_with_roots.check_read(Path("/etc/passwd").resolve())


def test_check_read_exact_root(guard_with_roots: PathGuard, tmp_path: Path) -> None:
    result = guard_with_roots.check_read(tmp_path.resolve())
    assert result == tmp_path.resolve()


def test_check_write_allowed(guard_with_roots: PathGuard, tmp_path: Path) -> None:
    f = tmp_path / "out.txt"
    result = guard_with_roots.check_write(f.resolve())
    assert result == f.resolve()


def test_check_write_denied(guard_with_roots: PathGuard) -> None:
    with pytest.raises(PermissionError, match="Write denied"):
        guard_with_roots.check_write(Path("/etc/shadow").resolve())


def test_resolve_read_composite(guard_with_roots: PathGuard, tmp_path: Path) -> None:
    (tmp_path / "data.csv").write_text("a,b")
    result = guard_with_roots.resolve_read("data.csv", cwd=str(tmp_path))
    assert result == (tmp_path / "data.csv").resolve()


def test_dotdot_traversal_denied(guard_with_roots: PathGuard, tmp_path: Path) -> None:
    with pytest.raises(PermissionError):
        guard_with_roots.resolve_read(
            str(tmp_path / "subdir" / ".." / ".." / "etc" / "passwd"),
            cwd=str(tmp_path),
        )


def test_resolve_follows_final_symlink_by_default(
    guard_with_roots: PathGuard,
    tmp_path: Path,
) -> None:
    target = tmp_path / "target.txt"
    target.write_text("ok")
    link = tmp_path / "link.txt"
    link.symlink_to(target)

    result = guard_with_roots.resolve(str(link))
    assert result == target.resolve()


def test_resolve_write_preserves_final_component_for_symlink(
    guard_with_roots: PathGuard,
    tmp_path: Path,
) -> None:
    target = tmp_path / "target.txt"
    target.write_text("ok")
    link = tmp_path / "link.txt"
    link.symlink_to(target)

    result = guard_with_roots.resolve_write(str(link))
    assert result == link
