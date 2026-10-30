"""Audit high-impact capabilities from an inspect-style authoring bundle."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

from nextmcp.nextflow_schema import flatten_nextflow_schema

ROUTE_NAME_KEYWORDS = (
    "aligner",
    "pseudo",
    "umi",
    "kraken",
    "bracken",
    "contaminant",
    "trim",
    "dedup",
    "skip",
    "with_",
    "enable",
    "disable",
    "mode",
    "method",
)
PREREQUISITE_KEYWORDS = (
    "license",
    "sentieon",
    "database",
    "prebuilt",
    "pre-built",
    "index",
    "secret",
)
OUTPUT_KEYWORDS = (
    "multiqc",
    "report",
    "bam",
    "matrix",
    "counts",
    "quantification",
    "salmon",
    "stringtie",
    "contamination",
)
STEP_PATTERN = re.compile(r"\bSTEP_[A-Z0-9_]+\b")
PUBLISH_PATTERN = re.compile(r"\bpublishDir\b|\bpath\s+['\"]([^'\"]+)['\"]")


def audit_capabilities(bundle: dict[str, Any]) -> dict[str, Any]:
    """Return a structured capability audit for one authoring bundle."""
    pipeline_id = _string_value(bundle.get("pipeline_id"), default="unknown")
    capabilities: dict[str, dict[str, Any]] = {}

    schema = bundle.get("schema")
    if isinstance(schema, dict):
        flattened = flatten_nextflow_schema(schema)
        for name, field_schema in sorted(flattened.properties.items()):
            if not isinstance(field_schema, dict):
                continue
            _audit_schema_parameter(
                capabilities=capabilities,
                name=name,
                field_schema=field_schema,
                required=name in flattened.required,
            )

    for item in _file_entries(bundle.get("source_files")):
        role = _string_value(item.get("role"), default="source_file")
        path = _string_value(item.get("path"), default="<unknown source>")
        content = _string_value(item.get("content"), default="")
        _audit_source_file(
            capabilities=capabilities,
            role=role,
            path=path,
            content=content,
        )

    for item in _file_entries(bundle.get("documents")):
        role = _string_value(item.get("role"), default="document")
        path = _string_value(item.get("path"), default="<unknown document>")
        content = _string_value(item.get("content"), default="")
        _audit_document(
            capabilities=capabilities,
            role=role,
            path=path,
            content=content,
        )

    ordered = sorted(
        capabilities.values(),
        key=lambda item: (0 if item["impact"] == "high" else 1, item["id"]),
    )
    return {
        "pipeline_id": pipeline_id,
        "status": "needs_review"
        if any(item["status"] == "needs_review" for item in ordered)
        else "covered",
        "summary": {
            "total": len(ordered),
            "high_impact": sum(1 for item in ordered if item["impact"] == "high"),
            "needs_review": sum(1 for item in ordered if item["status"] == "needs_review"),
        },
        "capabilities": ordered,
    }


def _audit_schema_parameter(
    *,
    capabilities: dict[str, dict[str, Any]],
    name: str,
    field_schema: dict[str, Any],
    required: bool,
) -> None:
    lowered_name = name.lower()
    description = _description_for_field(field_schema)
    lowered_text = f"{lowered_name} {description.lower()}"
    enum = field_schema.get("enum")
    normalized_type = field_schema.get("type")

    if (
        _is_boolean_type(normalized_type)
        or isinstance(enum, list)
        or _contains_any(lowered_text, ROUTE_NAME_KEYWORDS)
    ):
        required_assets = ["playbooks.yaml", "param-presets.yaml"]
        if _contains_any(lowered_text, OUTPUT_KEYWORDS):
            required_assets.append("artifact-contracts.yaml")
        _add_capability(
            capabilities,
            capability_id=f"schema_param_{_slug(name)}",
            label=f"Schema parameter `{name}` may change run planning.",
            kind="schema_parameter",
            impact="high"
            if required or _is_boolean_type(normalized_type) or isinstance(enum, list)
            else "medium",
            required_assets=required_assets,
            evidence={
                "source": "schema",
                "path": "nextflow_schema.json",
                "field": name,
                "excerpt": description,
            },
        )

    if _contains_any(lowered_text, PREREQUISITE_KEYWORDS):
        _add_capability(
            capabilities,
            capability_id=f"prerequisite_{_slug(name)}",
            label=f"Parameter `{name}` suggests a runtime prerequisite.",
            kind="runtime_prerequisite",
            impact="high",
            required_assets=["playbooks.yaml", "param-presets.yaml", "qc-rules.yaml"],
            evidence={
                "source": "schema",
                "path": "nextflow_schema.json",
                "field": name,
                "excerpt": description,
            },
        )


def _audit_source_file(
    *,
    capabilities: dict[str, dict[str, Any]],
    role: str,
    path: str,
    content: str,
) -> None:
    if role == "entry_script" or path.endswith("interactive.nf"):
        _add_capability(
            capabilities,
            capability_id=f"alternate_entry_{_slug(Path(path).name)}",
            label=f"Alternate entry script `{path}` needs an explicit step recipe.",
            kind="alternate_entry",
            impact="high",
            required_assets=["pipeline-profile.yaml", "step-recipes.yaml", "playbooks.yaml"],
            evidence={"source": "source_files", "path": path, "excerpt": _first_line(content)},
        )

    for step_name in sorted(set(STEP_PATTERN.findall(content))):
        _add_capability(
            capabilities,
            capability_id=f"step_entry_{_slug(step_name)}",
            label=f"Step workflow `{step_name}` should be covered or scoped out.",
            kind="step_entry",
            impact="high",
            required_assets=["pipeline-profile.yaml", "step-recipes.yaml", "playbooks.yaml"],
            evidence={"source": "source_files", "path": path, "excerpt": step_name},
        )

    if PUBLISH_PATTERN.search(content):
        _add_capability(
            capabilities,
            capability_id=f"published_outputs_{_slug(Path(path).stem)}",
            label=f"Published outputs in `{path}` should be reflected in artifact contracts.",
            kind="published_outputs",
            impact="medium",
            required_assets=["artifact-contracts.yaml", "qc-rules.yaml"],
            evidence={
                "source": "source_files",
                "path": path,
                "excerpt": "publishDir or path output",
            },
        )


def _audit_document(
    *,
    capabilities: dict[str, dict[str, Any]],
    role: str,
    path: str,
    content: str,
) -> None:
    del role
    lowered = content.lower()
    for keyword in OUTPUT_KEYWORDS:
        if keyword in lowered:
            _add_capability(
                capabilities,
                capability_id=f"documented_output_{_slug(keyword)}",
                label=f"Documented `{keyword}` outputs need artifact and review guidance.",
                kind="documented_output",
                impact="medium",
                required_assets=["artifact-contracts.yaml", "qc-rules.yaml"],
                evidence={"source": "documents", "path": path, "excerpt": keyword},
            )
    for keyword in PREREQUISITE_KEYWORDS:
        if keyword in lowered:
            _add_capability(
                capabilities,
                capability_id=f"documented_prerequisite_{_slug(keyword)}",
                label=f"Documented `{keyword}` prerequisite should be explicit in planning.",
                kind="runtime_prerequisite",
                impact="high",
                required_assets=["playbooks.yaml", "param-presets.yaml", "qc-rules.yaml"],
                evidence={"source": "documents", "path": path, "excerpt": keyword},
            )


def _add_capability(
    capabilities: dict[str, dict[str, Any]],
    *,
    capability_id: str,
    label: str,
    kind: str,
    impact: str,
    required_assets: list[str],
    evidence: dict[str, str],
) -> None:
    item = capabilities.get(capability_id)
    if item is None:
        capabilities[capability_id] = {
            "id": capability_id,
            "label": label,
            "kind": kind,
            "impact": impact,
            "status": "needs_review",
            "required_assets": sorted(set(required_assets)),
            "coverage": [],
            "scope_out_reason": None,
            "evidence": [evidence],
        }
        return
    if impact == "high":
        item["impact"] = "high"
    item["required_assets"] = sorted(set(item["required_assets"]) | set(required_assets))
    item["evidence"].append(evidence)


def _file_entries(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _contains_any(value: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in value for keyword in keywords)


def _is_boolean_type(raw_type: Any) -> bool:
    if raw_type == "boolean":
        return True
    return isinstance(raw_type, list) and "boolean" in raw_type


def _description_for_field(field_schema: dict[str, Any]) -> str:
    for key in ("description", "help_text", "title"):
        value = field_schema.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "No current schema description provided."


def _string_value(value: Any, *, default: str) -> str:
    return value if isinstance(value, str) and value.strip() else default


def _first_line(value: str) -> str:
    for line in value.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:160]
    return ""


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "unknown"


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit capabilities from an authoring bundle.")
    parser.add_argument(
        "--bundle", required=True, help="Path to an inspect-style authoring bundle JSON."
    )
    parser.add_argument("--output", help="Optional YAML output path. Prints YAML when omitted.")
    args = parser.parse_args()

    bundle = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
    if not isinstance(bundle, dict):
        raise ValueError("authoring bundle JSON must parse to an object")
    payload = audit_capabilities(bundle)

    if args.output:
        _write_yaml(Path(args.output), payload)
    else:
        print(yaml.safe_dump(payload, sort_keys=False), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
