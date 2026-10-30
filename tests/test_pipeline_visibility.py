"""Tests for nextmcp.pipeline_visibility."""

from __future__ import annotations

from pathlib import Path

import pytest

from nextmcp.pipeline_visibility import _path_or_none


def test_path_or_none_tolerates_unresolvable_home_directory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A "~"-leading string must not abort redaction.

    pathlib raises RuntimeError, not OSError, when it cannot resolve a leading
    "~" because the process has no home directory. Nextflow's task polling block
    ("~> TaskHandler[...]") produces exactly such lines, and run_get/run_logs
    feed every log line through this helper.
    """

    def _raise(self: Path) -> Path:
        raise RuntimeError("Could not determine home directory.")

    monkeypatch.setattr(Path, "expanduser", _raise)

    assert _path_or_none("~> TaskHandler[id: 1; name: DEMO (sample)]") is None


def test_path_or_none_tolerates_oserror(monkeypatch: pytest.MonkeyPatch) -> None:
    """Filesystem errors keep returning None rather than propagating."""

    def _raise(self: Path) -> Path:
        raise OSError("invalid path")

    monkeypatch.setattr(Path, "expanduser", _raise)

    assert _path_or_none("/some/path") is None


def test_path_or_none_ignores_multi_line_values() -> None:
    assert _path_or_none("first line\nsecond line") is None


def test_path_or_none_resolves_ordinary_paths(tmp_path: Path) -> None:
    assert _path_or_none(str(tmp_path)) == tmp_path.resolve()
