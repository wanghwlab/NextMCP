"""Check capability exclusions without accepting unresolved audit entries."""

import importlib.util
from pathlib import Path

import pytest
import yaml


@pytest.mark.parametrize(
    ("status", "reason", "expected"),
    [
        ("scoped_out", "Not part of the official release.", "pass"),
        ("scoped_out", None, "fail"),
        ("needs_review", None, "fail"),
    ],
)
def test_capability_scope_requires_reason(
    tmp_path: Path, status: str, reason: str | None, expected: str
) -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "skills/meta/pipeline-expert-skill-creator/scripts/validate_expert_skill.py"
    )
    spec = importlib.util.spec_from_file_location("scope_validator", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "capability-audit.yaml").write_text(
        yaml.safe_dump(
            {
                "capabilities": [
                    {"id": "optional_mode", "status": status, "scope_out_reason": reason}
                ]
            }
        ),
        encoding="utf-8",
    )
    checks: list[dict[str, object]] = []
    module._check_capability_coverage(skill_root=tmp_path, checks=checks)
    assert checks[0]["status"] == expected
