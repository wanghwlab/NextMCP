"""Validate machine-checkable parts of a generated pipeline expert skill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from nextmcp.nextflow_schema import flatten_nextflow_schema

REQUIRED_FILES = (
    "SKILL.md",
    "assets/pipeline-profile.yaml",
    "assets/playbooks.yaml",
    "assets/step-recipes.yaml",
    "assets/param-presets.yaml",
    "assets/schema-index.yaml",
    "assets/capability-audit.yaml",
    "assets/authoring-gaps.yaml",
    "assets/artifact-contracts.yaml",
    "assets/qc-rules.yaml",
    "references/01_scope_and_assumptions.md",
    "references/02_playbooks.md",
    "references/03_parameters.md",
    "references/04_schema_lookup.md",
    "references/05_outputs_and_qc.md",
    "references/06_troubleshooting.md",
)
REQUIRED_DIRS = (
    "assets/schema-groups",
    "references/schema-groups",
)
FORBIDDEN_RUNTIME_TOKENS = (
    'nextflow_inspect_pipeline(detail="materials")',
    "nextflow_inspect_pipeline(detail='materials')",
    "nextflow_get_schema",
    "nextflow_get_pipeline",
    "resume_session_id",
)
REQUIRED_RUNTIME_TOKENS = (
    "nextmcp server filesystem",
    "server-local",
    "run_get(include=[",
    "from_run_id",
)
CAPABILITY_ASSET_MAP = {
    "pipeline-profile.yaml": ("assets/pipeline-profile.yaml",),
    "playbooks.yaml": ("assets/playbooks.yaml",),
    "step-recipes.yaml": ("assets/step-recipes.yaml",),
    "param-presets.yaml": ("assets/param-presets.yaml",),
    "artifact-contracts.yaml": ("assets/artifact-contracts.yaml",),
    "qc-rules.yaml": ("assets/qc-rules.yaml",),
}


def validate_expert_skill(
    *,
    skill_root: Path,
    bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    """Validate one expert skill source package."""
    checks: list[dict[str, Any]] = []
    skill_root = skill_root.resolve()

    _check_layout(skill_root=skill_root, checks=checks)
    runtime_content = _runtime_content(skill_root)
    _check_runtime_boundaries(runtime_content=runtime_content, checks=checks)
    _check_schema_coverage(skill_root=skill_root, bundle=bundle, checks=checks)
    _check_capability_coverage(skill_root=skill_root, checks=checks)
    _check_authoring_gaps(skill_root=skill_root, checks=checks)

    failed = [check for check in checks if check["status"] == "fail"]
    manual = [check for check in checks if check["status"] == "manual_review"]
    return {
        "skill_root": str(skill_root),
        "status": "fail" if failed else "pass",
        "summary": {
            "checks": len(checks),
            "failed": len(failed),
            "manual_review": len(manual),
        },
        "checks": checks,
    }


def _check_layout(*, skill_root: Path, checks: list[dict[str, Any]]) -> None:
    missing_files = [path for path in REQUIRED_FILES if not (skill_root / path).is_file()]
    missing_dirs = [path for path in REQUIRED_DIRS if not (skill_root / path).is_dir()]
    _add_check(
        checks,
        check_id="layout",
        status="fail" if missing_files or missing_dirs else "pass",
        message="Required expert skill files and directories are present.",
        evidence={"missing_files": missing_files, "missing_directories": missing_dirs},
    )


def _check_runtime_boundaries(*, runtime_content: str, checks: list[dict[str, Any]]) -> None:
    forbidden_found = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in runtime_content]
    required_missing = [token for token in REQUIRED_RUNTIME_TOKENS if token not in runtime_content]
    _add_check(
        checks,
        check_id="runtime-boundaries",
        status="fail" if forbidden_found or required_missing else "pass",
        message="Runtime guidance keeps authoring tools out and preserves path/restart boundaries.",
        evidence={
            "forbidden_found": forbidden_found,
            "required_missing": required_missing,
        },
    )


def _check_schema_coverage(
    *,
    skill_root: Path,
    bundle: dict[str, Any] | None,
    checks: list[dict[str, Any]],
) -> None:
    if bundle is None:
        _add_check(
            checks,
            check_id="schema-coverage",
            status="manual_review",
            message="No authoring bundle was provided, so exact schema coverage was not checked.",
            evidence={},
        )
        return

    schema = bundle.get("schema")
    if not isinstance(schema, dict):
        _add_check(
            checks,
            check_id="schema-coverage",
            status="fail",
            message="Authoring bundle does not include a parsed schema object.",
            evidence={},
        )
        return

    expected = set(flatten_nextflow_schema(schema).properties)
    observed: dict[str, str] = {}
    duplicates: dict[str, list[str]] = {}
    for path in sorted((skill_root / "assets" / "schema-groups").glob("*.yaml")):
        payload = _read_yaml(path)
        if not isinstance(payload, dict):
            continue
        params = payload.get("parameters")
        if not isinstance(params, list):
            continue
        for item in params:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            if not isinstance(name, str):
                continue
            if name in observed:
                duplicates.setdefault(name, [observed[name]]).append(str(path))
            observed[name] = str(path)

    missing = sorted(expected - set(observed))
    extra = sorted(set(observed) - expected)
    _add_check(
        checks,
        check_id="schema-coverage",
        status="fail" if missing or extra or duplicates else "pass",
        message="Every current schema parameter appears in exactly one grouped schema asset.",
        evidence={
            "missing": missing,
            "extra": extra,
            "duplicates": duplicates,
            "expected_count": len(expected),
            "observed_count": len(observed),
        },
    )


def _check_capability_coverage(*, skill_root: Path, checks: list[dict[str, Any]]) -> None:
    path = skill_root / "assets" / "capability-audit.yaml"
    payload = _read_yaml(path)
    if not isinstance(payload, dict):
        _add_check(
            checks,
            check_id="capability-coverage",
            status="fail",
            message="Capability audit is missing or invalid.",
            evidence={"path": str(path)},
        )
        return

    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, list):
        capabilities = []

    failures: list[dict[str, Any]] = []
    for item in capabilities:
        if not isinstance(item, dict):
            continue
        status = item.get("status")
        if status == "scoped_out":
            if not item.get("scope_out_reason"):
                failures.append({"id": item.get("id"), "reason": "scoped_out without reason"})
            continue
        if status != "covered":
            failures.append({"id": item.get("id"), "reason": f"status is {status!r}"})
            continue
        missing_assets = _missing_capability_assets(skill_root=skill_root, capability=item)
        if missing_assets:
            failures.append(
                {
                    "id": item.get("id"),
                    "reason": "covered capability lacks asset evidence",
                    "missing_assets": missing_assets,
                }
            )

    _add_check(
        checks,
        check_id="capability-coverage",
        status="fail" if failures else "pass",
        message="High-impact capabilities are covered or explicitly scoped out.",
        evidence={"failures": failures, "capability_count": len(capabilities)},
    )


def _missing_capability_assets(*, skill_root: Path, capability: dict[str, Any]) -> list[str]:
    required_assets = capability.get("required_assets")
    if not isinstance(required_assets, list):
        return []
    needle = str(capability.get("id") or capability.get("label") or "").lower()
    coverage = capability.get("coverage")
    coverage_text = (
        " ".join(str(item).lower() for item in coverage) if isinstance(coverage, list) else ""
    )
    missing: list[str] = []
    for asset in required_assets:
        if not isinstance(asset, str):
            continue
        paths = CAPABILITY_ASSET_MAP.get(asset)
        if paths is None:
            continue
        asset_content = "\n".join(
            (skill_root / relative_path).read_text(encoding="utf-8")
            for relative_path in paths
            if (skill_root / relative_path).is_file()
        ).lower()
        if needle and needle in asset_content:
            continue
        if asset.lower() in coverage_text:
            continue
        missing.append(asset)
    return missing


def _check_authoring_gaps(*, skill_root: Path, checks: list[dict[str, Any]]) -> None:
    path = skill_root / "assets" / "authoring-gaps.yaml"
    payload = _read_yaml(path)
    if not isinstance(payload, dict):
        _add_check(
            checks,
            check_id="authoring-gaps",
            status="fail",
            message="Authoring gaps file is missing or invalid.",
            evidence={"path": str(path)},
        )
        return
    gaps = payload.get("gaps")
    open_gaps = (
        [
            item
            for item in gaps
            if isinstance(item, dict) and item.get("status") not in {"resolved", "scoped_out"}
        ]
        if isinstance(gaps, list)
        else []
    )
    _add_check(
        checks,
        check_id="authoring-gaps",
        status="fail" if open_gaps else "pass",
        message="Starter scaffold gaps are resolved or explicitly scoped out.",
        evidence={"open_gaps": open_gaps},
    )


def _runtime_content(skill_root: Path) -> str:
    paths = [
        skill_root / "SKILL.md",
        skill_root / "assets" / "playbooks.yaml",
        skill_root / "assets" / "step-recipes.yaml",
        skill_root / "references" / "02_playbooks.md",
        skill_root / "references" / "03_parameters.md",
        skill_root / "references" / "05_outputs_and_qc.md",
        skill_root / "references" / "06_troubleshooting.md",
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths if path.is_file())


def _read_yaml(path: Path) -> Any:
    if not path.is_file():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _add_check(
    checks: list[dict[str, Any]],
    *,
    check_id: str,
    status: str,
    message: str,
    evidence: dict[str, Any],
) -> None:
    checks.append(
        {
            "id": check_id,
            "status": status,
            "message": message,
            "evidence": evidence,
        }
    )


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Expert Skill Validation Report",
        "",
        f"- Status: `{report['status']}`",
        f"- Failed checks: {report['summary']['failed']}",
        f"- Manual review checks: {report['summary']['manual_review']}",
        "",
        "## Checks",
        "",
    ]
    for check in report["checks"]:
        lines.extend(
            [
                f"### {check['id']}",
                "",
                f"- Status: `{check['status']}`",
                f"- Message: {check['message']}",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a generated pipeline expert skill.")
    parser.add_argument(
        "--skill-root", required=True, help="Path to a <pipeline>-expert-skill directory."
    )
    parser.add_argument(
        "--bundle", help="Optional authoring bundle JSON for schema coverage checks."
    )
    parser.add_argument("--json-output", help="Optional JSON report path.")
    parser.add_argument("--markdown-output", help="Optional Markdown report path.")
    args = parser.parse_args()

    bundle = None
    if args.bundle:
        loaded = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("authoring bundle JSON must parse to an object")
        bundle = loaded

    report = validate_expert_skill(skill_root=Path(args.skill_root), bundle=bundle)

    if args.json_output:
        json_path = Path(args.json_output)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
        )
    if args.markdown_output:
        markdown_path = Path(args.markdown_output)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(_render_markdown(report) + "\n", encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(json.dumps(report, indent=2, ensure_ascii=True))
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
