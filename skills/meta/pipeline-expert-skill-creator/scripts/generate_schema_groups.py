"""Generate progressive-disclosure schema assets for a pipeline expert skill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from nextmcp.nextflow_schema import flatten_nextflow_schema

FALLBACK_GROUP_ORDER = (
    "input_paths_and_manifests",
    "references_and_indices",
    "route_selectors_and_booleans",
    "enums_and_choice_params",
    "outputs_and_reporting",
    "tuning_metadata_and_notifications",
)
CLASSIFICATION_ORDER = {
    "route_shaping": 0,
    "lookup_only": 1,
    "non_runtime": 2,
}
VALID_CLASSIFICATIONS = set(CLASSIFICATION_ORDER)
VALID_CHANNELS = {"params", "config_files", "runtime_metadata", "authoring_only"}
RULES_PATH = Path(__file__).resolve().parents[1] / "assets" / "schema-grouping-rules.yaml"


def generate_schema_group_artifacts(
    schema: dict[str, Any],
    *,
    pipeline_id: str | None,
    overrides: dict[str, Any] | None,
    rules: dict[str, Any] | None = None,
    write_reference_drafts: bool = False,
) -> dict[str, Any]:
    """Generate grouped schema assets and optional grouped reference drafts."""
    grouping_rules = rules if rules is not None else _load_yaml(RULES_PATH)
    override_map = overrides if overrides is not None else {}

    flattened = flatten_nextflow_schema(schema)
    source_sections = _collect_source_sections(schema)
    group_ids, group_meta, structured_param_groups = _resolve_group_layout(
        schema=schema,
        rules=grouping_rules,
        overrides=override_map,
    )
    grouped_params: dict[str, list[dict[str, Any]]] = {group_id: [] for group_id in group_ids}

    for name in sorted(flattened.properties):
        field_schema = flattened.properties[name]
        group_id = _assign_group(
            name=name,
            field_schema=field_schema,
            rules=grouping_rules,
            overrides=override_map,
            available_group_ids=group_ids,
            structured_param_groups=structured_param_groups,
        )
        payload = _build_parameter_payload(
            name=name,
            field_schema=field_schema,
            required=name in flattened.required,
            group_id=group_id,
            group_meta=group_meta[group_id],
            pipeline_id=pipeline_id,
            source_section=source_sections.get(name),
            rules=grouping_rules,
            overrides=override_map,
        )
        grouped_params[group_id].append(payload)

    group_payloads: dict[str, dict[str, Any]] = {}
    for group_id in group_ids:
        params = sorted(
            grouped_params[group_id],
            key=lambda item: (CLASSIFICATION_ORDER[item["classification"]], item["name"]),
        )
        group_payloads[group_id] = {
            "group": {
                "id": group_id,
                "label": group_meta[group_id]["label"],
                "selection_rule": group_meta[group_id]["selection_rule"],
                "lookup_order": [
                    "assets/schema-index.yaml",
                    f"references/schema-groups/{group_id}.md",
                    f"assets/schema-groups/{group_id}.yaml",
                ],
                "coverage_notes": group_meta[group_id]["coverage_notes"],
            },
            "parameters": params,
        }

    grouping_strategy = override_map.get("grouping_strategy")
    if not isinstance(grouping_strategy, str) or not grouping_strategy.strip():
        if structured_param_groups:
            base = "schema top-level sections from nextflow_schema.json allOf order"
        else:
            base = "default heuristic schema groups from pipeline-expert-skill-creator generator v1"
        grouping_strategy = f"{base} for {pipeline_id}" if pipeline_id else base

    schema_index = {
        "grouping_strategy": grouping_strategy,
        "groups": [
            {
                "id": group_id,
                "label": group_meta[group_id]["label"],
                "use_when": group_meta[group_id]["use_when"],
                "summary": group_meta[group_id]["coverage_notes"],
                "asset_path": f"assets/schema-groups/{group_id}.yaml",
                "reference_path": f"references/schema-groups/{group_id}.md",
                "parameter_count": len(group_payloads[group_id]["parameters"]),
            }
            for group_id in group_ids
        ],
    }

    reference_drafts: dict[str, str] = {}
    if write_reference_drafts:
        for group_id in group_ids:
            reference_drafts[group_id] = _render_group_reference(
                group_id=group_id,
                group_payload=group_payloads[group_id],
                use_when=group_meta[group_id]["use_when"],
            )

    return {
        "schema_index": schema_index,
        "group_payloads": group_payloads,
        "reference_drafts": reference_drafts,
    }


def _resolve_group_layout(
    *,
    schema: dict[str, Any],
    rules: dict[str, Any],
    overrides: dict[str, Any],
) -> tuple[list[str], dict[str, dict[str, str | None]], dict[str, str]]:
    structured_layout = _extract_structured_schema_group_layout(
        schema=schema,
        rules=rules,
        overrides=overrides,
    )
    if structured_layout is not None:
        return structured_layout

    group_meta = _group_metadata(rules, overrides)
    return list(group_meta), group_meta, {}


def write_schema_group_artifacts(
    *,
    output_root: Path,
    schema_index: dict[str, Any],
    group_payloads: dict[str, dict[str, Any]],
    reference_drafts: dict[str, str] | None,
) -> None:
    """Write generated grouped schema assets under one expert skill root."""
    assets_dir = output_root / "assets"
    group_dir = assets_dir / "schema-groups"
    group_dir.mkdir(parents=True, exist_ok=True)
    _write_yaml(assets_dir / "schema-index.yaml", schema_index)

    for group_id, payload in group_payloads.items():
        _write_yaml(group_dir / f"{group_id}.yaml", payload)

    if reference_drafts:
        references_dir = output_root / "references" / "schema-groups"
        references_dir.mkdir(parents=True, exist_ok=True)
        for group_id, content in reference_drafts.items():
            (references_dir / f"{group_id}.md").write_text(content, encoding="utf-8")


def _extract_structured_schema_group_layout(
    *,
    schema: dict[str, Any],
    rules: dict[str, Any],
    overrides: dict[str, Any],
) -> tuple[list[str], dict[str, dict[str, str | None]], dict[str, str]] | None:
    all_of = schema.get("allOf")
    if not isinstance(all_of, list) or not all_of:
        return None

    group_overrides = overrides.get("group_overrides")
    if not isinstance(group_overrides, dict):
        group_overrides = {}

    ordered_group_ids: list[str] = []
    group_meta: dict[str, dict[str, str | None]] = {}
    param_to_group: dict[str, str] = {}

    for item in all_of:
        if not isinstance(item, dict):
            continue
        ref = item.get("$ref")
        if not isinstance(ref, str) or not ref.startswith("#/"):
            continue

        resolved = _resolve_schema_node(item, root=schema)
        flattened = flatten_nextflow_schema(resolved)
        if not flattened.properties:
            continue

        group_id = ref.split("/")[-1]
        override = group_overrides.get(group_id)
        if override is not None and not isinstance(override, dict):
            raise ValueError(f"group_overrides[{group_id!r}] must be a mapping")

        title = resolved.get("title")
        label_default = (
            title.strip()
            if isinstance(title, str) and title.strip()
            else _humanize_identifier(group_id)
        )
        selection_title = title.strip() if isinstance(title, str) and title.strip() else group_id

        ordered_group_ids.append(group_id)
        group_meta[group_id] = {
            "label": _override_text(override, "label", label_default),
            "use_when": _override_text(
                override,
                "use_when",
                (
                    f"The runtime agent needs exact parameter mapping for the "
                    f"`{selection_title}` top-level section of the current `nextflow_schema.json`."
                ),
            ),
            "selection_rule": _override_text(
                override,
                "selection_rule",
                (
                    f"Use this group for parameters defined under the "
                    f"`{selection_title}` top-level schema section."
                ),
            ),
            "coverage_notes": _override_text(
                override,
                "coverage_notes",
                (
                    f"Preserves the original `nextflow_schema.json` top-level section "
                    f"`{group_id}` for exact lookup."
                ),
            ),
            "placeholder_root": _infer_section_placeholder_root(
                group_id=group_id,
                title=title,
                rules=rules,
            ),
        }

        for name in flattened.properties:
            existing_group = param_to_group.get(name)
            if existing_group is not None and existing_group != group_id:
                raise ValueError(
                    f"Parameter {name!r} appears in multiple top-level schema sections: "
                    f"{existing_group!r} and {group_id!r}"
                )
            param_to_group[name] = group_id

    if not ordered_group_ids:
        return None
    return ordered_group_ids, group_meta, param_to_group


def _group_metadata(
    rules: dict[str, Any],
    overrides: dict[str, Any],
) -> dict[str, dict[str, str | None]]:
    groups = rules.get("groups")
    if not isinstance(groups, list):
        raise ValueError("schema grouping rules must define a groups list")

    group_overrides = overrides.get("group_overrides")
    if not isinstance(group_overrides, dict):
        group_overrides = {}

    metadata: dict[str, dict[str, str | None]] = {}
    for raw_group in groups:
        if not isinstance(raw_group, dict):
            raise ValueError("schema grouping rules groups entries must be mappings")
        group_id = _require_string(raw_group, "id")
        override = group_overrides.get(group_id)
        if override is not None and not isinstance(override, dict):
            raise ValueError(f"group_overrides[{group_id!r}] must be a mapping")
        metadata[group_id] = {
            "label": _override_or_value(raw_group, override, "label"),
            "use_when": _override_or_value(raw_group, override, "use_when"),
            "selection_rule": _override_or_value(raw_group, override, "selection_rule"),
            "coverage_notes": _override_or_value(raw_group, override, "coverage_notes"),
            "placeholder_root": raw_group.get("placeholder_root"),
        }
    return metadata


def _assign_group(
    *,
    name: str,
    field_schema: dict[str, Any],
    rules: dict[str, Any],
    overrides: dict[str, Any],
    available_group_ids: list[str],
    structured_param_groups: dict[str, str],
) -> str:
    available_group_id_set = set(available_group_ids)
    parameter_override = _parameter_override(name, overrides)
    override_group_id = parameter_override.get("group_id")
    if isinstance(override_group_id, str):
        if override_group_id not in available_group_id_set:
            raise ValueError(f"Unsupported group override for {name!r}: {override_group_id}")
        return override_group_id

    force_groups = overrides.get("force_groups")
    if isinstance(force_groups, dict):
        forced = force_groups.get(name)
        if isinstance(forced, str):
            if forced not in available_group_id_set:
                raise ValueError(f"Unsupported forced group for {name!r}: {forced}")
            return forced

    if structured_param_groups:
        group_id = structured_param_groups.get(name)
        if group_id is None:
            raise ValueError(
                f"Could not resolve a top-level schema section for parameter {name!r}. "
                "Check the current nextflow_schema.json structure."
            )
        return group_id

    if field_schema.get("enum") is not None:
        return "enums_and_choice_params"
    if _is_boolean_schema(field_schema):
        return "route_selectors_and_booleans"
    if _looks_output_param(name=name, field_schema=field_schema, rules=rules):
        return "outputs_and_reporting"
    if _looks_reference_param(name=name, field_schema=field_schema, rules=rules):
        return "references_and_indices"
    if _looks_input_param(name=name, field_schema=field_schema, rules=rules):
        return "input_paths_and_manifests"
    if _looks_route_param(name=name, field_schema=field_schema, rules=rules):
        return "route_selectors_and_booleans"
    if _is_path_like(field_schema, rules):
        return "input_paths_and_manifests"
    return "tuning_metadata_and_notifications"


def _build_parameter_payload(
    *,
    name: str,
    field_schema: dict[str, Any],
    required: bool,
    group_id: str,
    group_meta: dict[str, str | None],
    pipeline_id: str | None,
    source_section: str | None,
    rules: dict[str, Any],
    overrides: dict[str, Any],
) -> dict[str, Any]:
    parameter_override = _parameter_override(name, overrides)
    classification = _classify_parameter(
        name=name,
        field_schema=field_schema,
        group_id=group_id,
        required=required,
        rules=rules,
        override=parameter_override,
    )
    channel = _determine_channel(
        name=name,
        classification=classification,
        rules=rules,
        override=parameter_override,
    )
    placeholder = _placeholder_for_parameter(
        name=name,
        field_schema=field_schema,
        group_id=group_id,
        group_meta=group_meta,
        pipeline_id=pipeline_id,
        channel=channel,
        rules=rules,
        override=parameter_override,
    )
    example_values = _example_values_for_parameter(
        field_schema=field_schema,
        placeholder=placeholder,
        override=parameter_override,
    )
    mapping_notes = _mapping_notes_for_parameter(
        name=name,
        group_id=group_id,
        channel=channel,
        classification=classification,
        field_schema=field_schema,
        rules=rules,
        override=parameter_override,
    )
    lookup_priority = _lookup_priority_for_parameter(
        required=required,
        classification=classification,
        override=parameter_override,
    )
    mapping_flags = _mapping_flags_for_parameter(field_schema)
    confidence = _confidence_for_parameter(
        field_schema=field_schema,
        override=parameter_override,
        mapping_flags=mapping_flags,
    )

    payload: dict[str, Any] = {
        "group_id": group_id,
        "name": name,
        "source_name": name,
        "type": _normalized_type(field_schema.get("type")),
        "required": required,
        "default": field_schema.get("default"),
        "enum": _normalized_enum(field_schema.get("enum")),
        "description": _description_for_field(field_schema),
        "classification": classification,
        "channel": channel,
        "placeholder": placeholder,
        "example_values": example_values,
        "mapping_notes": mapping_notes,
        "lookup_priority": lookup_priority,
        "confidence": confidence,
        "mapping_flags": mapping_flags,
    }
    if source_section is not None:
        payload["source_section"] = source_section
    payload["raw_schema"] = field_schema
    return payload


def _classify_parameter(
    *,
    name: str,
    field_schema: dict[str, Any],
    group_id: str,
    required: bool,
    rules: dict[str, Any],
    override: dict[str, Any],
) -> str:
    explicit = override.get("classification")
    if isinstance(explicit, str):
        if explicit not in VALID_CLASSIFICATIONS:
            raise ValueError(f"Unsupported classification override for {name!r}: {explicit}")
        return explicit

    if _looks_authoring_only(name=name, field_schema=field_schema, rules=rules):
        return "non_runtime"
    if field_schema.get("enum") is not None or _is_boolean_schema(field_schema):
        return "route_shaping"
    if _looks_route_param(name=name, field_schema=field_schema, rules=rules):
        return "route_shaping"
    if _looks_output_param(name=name, field_schema=field_schema, rules=rules):
        if name == "outdir" or name.startswith(("save_", "publish_")):
            return "route_shaping"
        return "lookup_only"
    if _looks_reference_param(name=name, field_schema=field_schema, rules=rules):
        return "route_shaping" if required or _is_path_like(field_schema, rules) else "lookup_only"
    if _looks_input_param(name=name, field_schema=field_schema, rules=rules):
        return "route_shaping" if required or _is_path_like(field_schema, rules) else "lookup_only"
    if required:
        return "route_shaping"
    return "lookup_only"


def _determine_channel(
    *,
    name: str,
    classification: str,
    rules: dict[str, Any],
    override: dict[str, Any],
) -> str:
    explicit = override.get("channel")
    if isinstance(explicit, str):
        if explicit not in VALID_CHANNELS:
            raise ValueError(f"Unsupported channel override for {name!r}: {explicit}")
        return explicit

    config_scope_names = _string_list(rules.get("heuristics", {}).get("config_scope_names"))
    if name in config_scope_names:
        return "config_files"
    if classification == "non_runtime":
        return "authoring_only"
    return "params"


def _placeholder_for_parameter(
    *,
    name: str,
    field_schema: dict[str, Any],
    group_id: str,
    group_meta: dict[str, str | None],
    pipeline_id: str | None,
    channel: str,
    rules: dict[str, Any],
    override: dict[str, Any],
) -> str | None:
    explicit = override.get("placeholder")
    if isinstance(explicit, str):
        return explicit

    if channel == "authoring_only":
        return None
    if channel == "config_files":
        return "<server_input_root>/resource_override.config"

    if name == "outdir":
        return (
            f"<server_output_root>/{pipeline_id}"
            if pipeline_id
            else "<server_output_root>/pipeline-results"
        )

    root = group_meta.get("placeholder_root")
    if not isinstance(root, str):
        if _looks_reference_param(name=name, field_schema=field_schema, rules=rules):
            root = _placeholder_root_for_group("references_and_indices", rules)
        elif _looks_input_param(name=name, field_schema=field_schema, rules=rules):
            root = _placeholder_root_for_group("input_paths_and_manifests", rules)
        elif _looks_output_param(
            name=name, field_schema=field_schema, rules=rules
        ) and _is_path_like(field_schema, rules):
            root = _placeholder_root_for_group("outputs_and_reporting", rules)
    if not isinstance(root, str):
        return None
    basename = _placeholder_basename(name=name, field_schema=field_schema, group_id=group_id)
    return f"{root}/{basename}"


def _placeholder_basename(*, name: str, field_schema: dict[str, Any], group_id: str) -> str:
    lowered_name = name.lower()
    if group_id == "references_and_indices":
        if "gtf" in lowered_name:
            return "genes.gtf"
        if "bed" in lowered_name:
            return "targets.bed"
        if "db" in lowered_name or "database" in lowered_name:
            return "database"
        if "index" in lowered_name:
            return "index"
        return "reference.fa"

    if "sheet" in lowered_name or "sample" in lowered_name:
        return "samplesheet.csv"
    if "manifest" in lowered_name:
        return "manifest.tsv"
    if "logo" in lowered_name:
        return "logo.png"
    if "config" in lowered_name:
        return "config.yaml"
    if "json" in lowered_name:
        return "params.json"
    if "fasta" in lowered_name:
        return "genome.fa"
    if "gtf" in lowered_name:
        return "genes.gtf"
    extension = _extension_hint(field_schema)
    if extension is not None:
        return f"{name}{extension}"
    return name


def _example_values_for_parameter(
    *,
    field_schema: dict[str, Any],
    placeholder: str | None,
    override: dict[str, Any],
) -> list[Any]:
    explicit = override.get("example_values")
    if isinstance(explicit, list):
        return explicit

    raw_enum = _normalized_enum(field_schema.get("enum"))
    if isinstance(raw_enum, list):
        return raw_enum[:3]
    if placeholder is not None:
        return [placeholder]
    if "default" in field_schema:
        return [field_schema["default"]]
    if _is_boolean_schema(field_schema):
        return [True, False]
    return []


def _mapping_notes_for_parameter(
    *,
    name: str,
    group_id: str,
    channel: str,
    classification: str,
    field_schema: dict[str, Any],
    rules: dict[str, Any],
    override: dict[str, Any],
) -> str:
    explicit = override.get("mapping_notes")
    if isinstance(explicit, str):
        return explicit

    if channel == "config_files":
        return (
            "Do not pass under `nextflow_run(params=...)`. Render this value into a small "
            "server-local override config and pass that file through "
            "`nextflow_run(config_files=...)`."
        )
    if channel == "authoring_only":
        return (
            "Preserved for exact schema coverage, but do not surface in ordinary nextmcp runtime "
            "planning unless the user explicitly asks for this helper or metadata field."
        )
    if field_schema.get("enum") is not None:
        return (
            "Map this value exactly to one current schema enum under `nextflow_run(params=...)`; "
            "do not invent spelling variants."
        )
    if _looks_reference_param(name=name, field_schema=field_schema, rules=rules):
        return (
            "Pass under `nextflow_run(params=...)` as a server-local reference, database, "
            "or prebuilt index value. Prefer reuse of confirmed server-side assets over "
            "rebuilding when appropriate."
        )
    if _is_path_like(field_schema, rules):
        return (
            "Pass under `nextflow_run(params=...)` as a server-local path or manifest-like value. "
            'Confirm the concrete path with `fs_list(mode="manifest")` when uncertain.'
        )
    if _looks_output_param(name=name, field_schema=field_schema, rules=rules):
        return (
            "Set only when the user wants a different output root, saved intermediate, "
            "or reporting "
            "behavior. Keep values in `params`, not `config_files`."
        )
    if classification == "route_shaping" or _looks_route_param(
        name=name, field_schema=field_schema, rules=rules
    ):
        return (
            "Pass under `nextflow_run(params=...)`. Check playbooks and step recipes before "
            "changing this route-shaping switch."
        )
    return "Preserve the current schema field name and pass under `nextflow_run(params=...)`."


def _lookup_priority_for_parameter(
    *,
    required: bool,
    classification: str,
    override: dict[str, Any],
) -> str:
    explicit = override.get("lookup_priority")
    if isinstance(explicit, str):
        return explicit
    if classification == "non_runtime":
        return "low"
    if required or classification == "route_shaping":
        return "high"
    return "medium"


def _mapping_flags_for_parameter(field_schema: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    for key in ("oneOf", "anyOf", "allOf"):
        value = field_schema.get(key)
        if isinstance(value, list) and value:
            flags.append(f"uses_{key}")
    normalized_type = _normalized_type(field_schema.get("type"))
    if isinstance(normalized_type, str) and normalized_type in {"object", "array"}:
        flags.append("needs_exact_lookup")
    if isinstance(normalized_type, list) and {"object", "array"} & set(normalized_type):
        flags.append("needs_exact_lookup")
    if field_schema.get("pattern") is not None:
        flags.append("has_pattern_constraint")
    return sorted(set(flags))


def _confidence_for_parameter(
    *,
    field_schema: dict[str, Any],
    override: dict[str, Any],
    mapping_flags: list[str],
) -> str:
    explicit = override.get("confidence")
    if isinstance(explicit, str) and explicit in {"low", "medium", "high"}:
        return explicit
    if mapping_flags:
        return "low"
    if field_schema.get("description") or field_schema.get("help_text"):
        return "high"
    return "medium"


def _looks_authoring_only(
    *, name: str, field_schema: dict[str, Any], rules: dict[str, Any]
) -> bool:
    heuristics = rules.get("heuristics", {})
    authoring_only_names = _string_list(heuristics.get("authoring_only_names"))
    authoring_only_prefixes = _string_list(heuristics.get("authoring_only_prefixes"))
    lowered_name = name.lower()
    if lowered_name in authoring_only_names:
        return True
    if any(lowered_name.startswith(prefix) for prefix in authoring_only_prefixes):
        return True
    description = _description_for_field(field_schema).lower()
    return any(
        keyword in description
        for keyword in _string_list(heuristics.get("non_runtime_description_keywords"))
    )


def _looks_input_param(*, name: str, field_schema: dict[str, Any], rules: dict[str, Any]) -> bool:
    heuristics = rules.get("heuristics", {})
    lowered_name = name.lower()
    description = _description_for_field(field_schema).lower()
    name_keywords = _string_list(heuristics.get("input_name_keywords"))
    description_keywords = _string_list(heuristics.get("input_description_keywords"))
    if any(keyword in lowered_name for keyword in name_keywords):
        return True
    if any(keyword in description for keyword in description_keywords):
        return True
    return _is_path_like(field_schema, rules)


def _looks_reference_param(
    *, name: str, field_schema: dict[str, Any], rules: dict[str, Any]
) -> bool:
    heuristics = rules.get("heuristics", {})
    lowered_name = name.lower()
    description = _description_for_field(field_schema).lower()
    name_keywords = _string_list(heuristics.get("reference_name_keywords"))
    description_keywords = _string_list(heuristics.get("reference_description_keywords"))
    return any(keyword in lowered_name for keyword in name_keywords) or any(
        keyword in description for keyword in description_keywords
    )


def _looks_output_param(*, name: str, field_schema: dict[str, Any], rules: dict[str, Any]) -> bool:
    heuristics = rules.get("heuristics", {})
    lowered_name = name.lower()
    description = _description_for_field(field_schema).lower()
    name_keywords = _string_list(heuristics.get("output_name_keywords"))
    description_keywords = _string_list(heuristics.get("output_description_keywords"))
    return any(keyword in lowered_name for keyword in name_keywords) or any(
        keyword in description for keyword in description_keywords
    )


def _looks_route_param(*, name: str, field_schema: dict[str, Any], rules: dict[str, Any]) -> bool:
    heuristics = rules.get("heuristics", {})
    lowered_name = name.lower()
    description = _description_for_field(field_schema).lower()
    name_keywords = _string_list(heuristics.get("route_name_keywords"))
    description_keywords = _string_list(heuristics.get("route_description_keywords"))
    return any(keyword in lowered_name for keyword in name_keywords) or any(
        keyword in description for keyword in description_keywords
    )


def _is_path_like(field_schema: dict[str, Any], rules: dict[str, Any]) -> bool:
    heuristics = rules.get("heuristics", {})
    path_formats = _string_list(heuristics.get("path_formats"))
    field_format = field_schema.get("format")
    return isinstance(field_format, str) and field_format in path_formats


def _is_boolean_schema(field_schema: dict[str, Any]) -> bool:
    normalized = _normalized_type(field_schema.get("type"))
    if isinstance(normalized, str):
        return normalized == "boolean"
    if isinstance(normalized, list):
        return "boolean" in normalized
    return False


def _normalized_type(raw_type: Any) -> str | list[str]:
    if raw_type is None:
        return "any"
    if isinstance(raw_type, str):
        return raw_type
    if isinstance(raw_type, list):
        normalized = [item for item in raw_type if isinstance(item, str)]
        if len(normalized) == 1:
            return normalized[0]
        if normalized:
            return normalized
    return "any"


def _normalized_enum(raw_enum: Any) -> list[Any] | None:
    if isinstance(raw_enum, list):
        return raw_enum
    return None


def _humanize_identifier(value: str) -> str:
    return " ".join(part.capitalize() for part in value.replace("-", "_").split("_") if part)


def _override_text(override: dict[str, Any] | None, field_name: str, default: str) -> str:
    if override is not None:
        value = override.get(field_name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


def _description_for_field(field_schema: dict[str, Any]) -> str:
    for key in ("description", "help_text", "title"):
        value = field_schema.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "No current schema description provided."


def _collect_source_sections(schema: dict[str, Any]) -> dict[str, str]:
    sections: dict[str, str] = {}
    _collect_source_sections_from_node(schema, root=schema, sections=sections, inherited_title=None)
    return sections


def _collect_source_sections_from_node(
    node: Any,
    *,
    root: dict[str, Any],
    sections: dict[str, str],
    inherited_title: str | None,
) -> None:
    resolved = _resolve_schema_node(node, root=root)
    current_title = inherited_title
    title = resolved.get("title")
    if isinstance(title, str) and title.strip():
        current_title = title.strip()

    raw_properties = resolved.get("properties")
    if isinstance(raw_properties, dict):
        for name, value in raw_properties.items():
            if isinstance(name, str) and isinstance(value, dict) and current_title is not None:
                sections.setdefault(name, current_title)

    raw_all_of = resolved.get("allOf")
    if not isinstance(raw_all_of, list):
        return
    for item in raw_all_of:
        _collect_source_sections_from_node(
            item,
            root=root,
            sections=sections,
            inherited_title=current_title,
        )


def _resolve_schema_node(node: Any, *, root: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(node, dict):
        raise ValueError("schema composition items must be mappings")
    ref = node.get("$ref")
    if ref is None:
        return node
    if not isinstance(ref, str) or not ref.startswith("#/"):
        raise ValueError(f"Unsupported schema $ref: {ref!r}")

    current: Any = root
    for part in ref[2:].split("/"):
        token = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or token not in current:
            raise ValueError(f"Unknown schema pointer: {ref}")
        current = current[token]
    if not isinstance(current, dict):
        raise ValueError(f"Expected mapping target for schema $ref: {ref}")
    return current


def _infer_section_placeholder_root(
    *,
    group_id: str,
    title: Any,
    rules: dict[str, Any],
) -> str | None:
    title_text = title.strip() if isinstance(title, str) and title.strip() else ""
    combined = f"{group_id} {title_text}".lower()
    if "reference" in combined:
        return _placeholder_root_for_group("references_and_indices", rules)
    if "output" in combined:
        return _placeholder_root_for_group("outputs_and_reporting", rules)
    if "input" in combined or "mandatory" in combined:
        return _placeholder_root_for_group("input_paths_and_manifests", rules)
    return None


def _placeholder_root_for_group(group_id: str, rules: dict[str, Any]) -> str | None:
    groups = rules.get("groups")
    if not isinstance(groups, list):
        return None
    for raw_group in groups:
        if not isinstance(raw_group, dict):
            continue
        raw_group_id = raw_group.get("id")
        if isinstance(raw_group_id, str) and raw_group_id == group_id:
            placeholder_root = raw_group.get("placeholder_root")
            if isinstance(placeholder_root, str):
                return placeholder_root
    return None


def _render_group_reference(
    *,
    group_id: str,
    group_payload: dict[str, Any],
    use_when: str,
) -> str:
    params = group_payload["parameters"]
    route_params = [param["name"] for param in params if param["classification"] == "route_shaping"]
    lookup_params = [param["name"] for param in params if param["classification"] == "lookup_only"]
    non_runtime_params = [
        param["name"] for param in params if param["classification"] == "non_runtime"
    ]

    lines = [
        f"# {group_payload['group']['label']}",
        "",
        use_when,
        "",
        group_payload["group"]["selection_rule"],
        "",
        f"- Exact source: `assets/schema-groups/{group_id}.yaml`",
        "- Discovery index: `assets/schema-index.yaml`",
        "",
        "## Route-shaping",
        "",
    ]
    lines.extend(
        _bullet_or_placeholder(
            route_params, "No route-shaping parameters were classified into this group."
        )
    )
    lines.extend(
        [
            "",
            "## Lookup-only",
            "",
        ]
    )
    lines.extend(
        _bullet_or_placeholder(
            lookup_params, "No lookup-only parameters were classified into this group."
        )
    )
    lines.extend(
        [
            "",
            "## Non-runtime",
            "",
        ]
    )
    lines.extend(
        _bullet_or_placeholder(
            non_runtime_params,
            "No non-runtime or authoring-only parameters were classified into this group.",
        )
    )
    return "\n".join(lines) + "\n"


def _bullet_or_placeholder(values: list[str], placeholder: str) -> list[str]:
    if not values:
        return [placeholder]
    return [f"- `{value}`" for value in values]


def _parameter_override(name: str, overrides: dict[str, Any]) -> dict[str, Any]:
    parameter_overrides = overrides.get("parameter_overrides")
    if not isinstance(parameter_overrides, dict):
        return {}
    override = parameter_overrides.get(name)
    if override is None:
        return {}
    if not isinstance(override, dict):
        raise ValueError(f"parameter_overrides[{name!r}] must be a mapping")
    return override


def _extension_hint(field_schema: dict[str, Any]) -> str | None:
    pattern = field_schema.get("pattern")
    if not isinstance(pattern, str):
        return None
    for extension in (
        ".csv",
        ".tsv",
        ".yaml",
        ".yml",
        ".json",
        ".txt",
        ".fa",
        ".fasta",
        ".gtf",
        ".bed",
    ):
        if extension.replace(".", "\\.") in pattern or extension in pattern:
            return extension
    return None


def _override_or_value(
    raw_group: dict[str, Any],
    override: dict[str, Any] | None,
    field_name: str,
) -> str:
    if override is not None:
        value = override.get(field_name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    value = raw_group.get(field_name)
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise ValueError(f"Missing required group metadata field: {field_name}")


def _require_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise ValueError(f"Expected non-empty string for {key}")


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping payload in {path}")
    return payload


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate progressive-disclosure schema assets for a pipeline expert skill."
    )
    parser.add_argument("--schema", required=True, help="Path to nextflow_schema.json")
    parser.add_argument(
        "--output-root",
        required=True,
        help=(
            "Expert skill root where assets/schema-index.yaml and "
            "assets/schema-groups/*.yaml will be written."
        ),
    )
    parser.add_argument(
        "--pipeline-id", help="Pipeline id used in grouping strategy and placeholders."
    )
    parser.add_argument(
        "--overrides", help="Optional YAML file with pipeline-specific grouping overrides."
    )
    parser.add_argument(
        "--rules", help="Optional grouping rules YAML. Defaults to the skill asset file."
    )
    parser.add_argument(
        "--write-reference-drafts",
        action="store_true",
        help="Also write references/schema-groups/*.md draft files.",
    )
    args = parser.parse_args()

    schema_path = Path(args.schema)
    output_root = Path(args.output_root)
    rules = _load_yaml(Path(args.rules)) if args.rules else None
    overrides = _load_yaml(Path(args.overrides)) if args.overrides else None
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    if not isinstance(schema, dict):
        raise ValueError("nextflow_schema.json must parse to a JSON object")

    artifacts = generate_schema_group_artifacts(
        schema,
        pipeline_id=args.pipeline_id,
        overrides=overrides,
        rules=rules,
        write_reference_drafts=args.write_reference_drafts,
    )
    write_schema_group_artifacts(
        output_root=output_root,
        schema_index=artifacts["schema_index"],
        group_payloads=artifacts["group_payloads"],
        reference_drafts=artifacts["reference_drafts"],
    )

    print(
        f"Generated {len(artifacts['schema_index']['groups'])} schema groups covering "
        f"{sum(group['parameter_count'] for group in artifacts['schema_index']['groups'])} "
        "parameters."
    )
    for group in artifacts["schema_index"]["groups"]:
        print(f"- {group['id']}: {group['parameter_count']} parameters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
