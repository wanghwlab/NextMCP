"""Helpers for lightweight Nextflow schema inspection and param validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FlattenedNextflowSchema:
    """Flattened top-level parameter constraints from a Nextflow schema."""

    properties: dict[str, dict[str, Any]]
    required: set[str]


def flatten_nextflow_schema(schema: dict[str, Any]) -> FlattenedNextflowSchema:
    """Collect top-level properties and required fields from a Nextflow schema."""
    if not isinstance(schema, dict):
        raise ValueError("nextflow schema must be a JSON object")

    properties: dict[str, dict[str, Any]] = {}
    required: set[str] = set()
    _merge_object_schema(schema, root=schema, properties=properties, required=required)
    return FlattenedNextflowSchema(properties=properties, required=required)


def validate_nextflow_params_against_schema(
    *,
    schema: dict[str, Any],
    params: dict[str, Any],
    allow_missing_required_from_external_sources: bool,
) -> dict[str, Any]:
    """Validate CLI params against generic required/type/default schema constraints."""
    flattened = flatten_nextflow_schema(schema)

    default_params = {
        name: field_schema["default"]
        for name, field_schema in flattened.properties.items()
        if name not in params and "default" in field_schema
    }

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    for name, value in params.items():
        field_schema = flattened.properties.get(name)
        if field_schema is None:
            continue

        expected_types = _normalize_schema_types(field_schema.get("type"))
        if not expected_types:
            continue
        if any(_matches_schema_type(value, expected_type) for expected_type in expected_types):
            continue

        errors.append(
            {
                "kind": "type_mismatch",
                "param": name,
                "expected": " or ".join(expected_types),
                "actual": _python_value_type(value),
            }
        )

    for name in sorted(flattened.required):
        if name in params or name in default_params:
            continue

        issue = {
            "kind": "missing_required",
            "param": name,
            "message": f"Required param `{name}` is missing from CLI params.",
        }
        if allow_missing_required_from_external_sources:
            warnings.append(issue)
        else:
            errors.append(issue)

    return {
        "available_defaults": default_params,
        "errors": errors,
        "warnings": warnings,
    }


def _merge_object_schema(
    schema: dict[str, Any],
    *,
    root: dict[str, Any],
    properties: dict[str, dict[str, Any]],
    required: set[str],
) -> None:
    """Merge one object-like schema node into the flattened view."""
    schema_type = schema.get("type")
    if schema_type == "object" or "properties" in schema or "required" in schema:
        raw_properties = schema.get("properties")
        if raw_properties is not None:
            if not isinstance(raw_properties, dict):
                raise ValueError("nextflow schema properties must be a JSON object")
            for name, field_schema in raw_properties.items():
                if isinstance(name, str) and isinstance(field_schema, dict):
                    properties[name] = field_schema

        raw_required = schema.get("required")
        if raw_required is not None:
            if not isinstance(raw_required, list):
                raise ValueError("nextflow schema required must be a JSON array")
            for item in raw_required:
                if isinstance(item, str):
                    required.add(item)

    raw_all_of = schema.get("allOf")
    if raw_all_of is None:
        return
    if not isinstance(raw_all_of, list):
        raise ValueError("nextflow schema allOf must be a JSON array")
    for item in raw_all_of:
        resolved = _resolve_schema_node(item, root=root)
        _merge_object_schema(resolved, root=root, properties=properties, required=required)


def _resolve_schema_node(node: Any, *, root: dict[str, Any]) -> dict[str, Any]:
    """Resolve one schema node or local $ref target."""
    if not isinstance(node, dict):
        raise ValueError("nextflow schema composition items must be JSON objects")

    ref = node.get("$ref")
    if ref is None:
        return node
    if not isinstance(ref, str) or not ref.startswith("#/"):
        raise ValueError(f"Unsupported nextflow schema $ref: {ref!r}")

    resolved = _resolve_json_pointer(root, ref[2:].split("/"))
    if not isinstance(resolved, dict):
        raise ValueError(f"Expected object target for nextflow schema $ref: {ref}")
    return resolved


def _resolve_json_pointer(payload: dict[str, Any], parts: list[str]) -> Any:
    """Resolve a local JSON pointer path."""
    current: Any = payload
    for part in parts:
        token = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or token not in current:
            raise ValueError(f"Unknown nextflow schema pointer: #/{'/'.join(parts)}")
        current = current[token]
    return current


def _normalize_schema_types(value: Any) -> list[str]:
    """Normalize a schema `type` field into a list of strings."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    raise ValueError("nextflow schema type must be a string or list of strings")


def _matches_schema_type(value: Any, expected_type: str) -> bool:
    """Check whether one Python value matches a JSON schema type."""
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return (isinstance(value, int) and not isinstance(value, bool)) or isinstance(value, float)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "null":
        return value is None
    return True


def _python_value_type(value: Any) -> str:
    """Return a JSON-schema-like type label for one Python value."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__
