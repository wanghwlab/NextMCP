"""Run offline evals.json prompts for a generated pipeline expert skill."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

import yaml

DEFAULT_TIMEOUT_SECONDS = 600
DEFAULT_AGENT = "claude"
DEFAULT_PROGRESS_INTERVAL_SECONDS = 30
SUPPORTED_AGENTS = {"claude", "codex", "kimi", "mock"}


def run_offline_evals(
    *,
    skill_root: Path,
    evals_path: Path | None,
    workspace: Path | None,
    iteration: str,
    agent: str,
    timeout_seconds: int,
    dry_run: bool,
    model: str | None = None,
    rerun_passed: bool = False,
    progress: bool = True,
    progress_interval_seconds: int = DEFAULT_PROGRESS_INTERVAL_SECONDS,
) -> dict[str, Any]:
    """Run one offline eval set and return a summary report."""
    if agent not in SUPPORTED_AGENTS:
        raise ValueError(f"Unsupported agent {agent!r}; choose one of {sorted(SUPPORTED_AGENTS)}")
    if model is not None and agent != "codex":
        raise ValueError("--model is currently supported only with --agent codex")

    skill_root = skill_root.resolve()
    evals_path = (evals_path or skill_root / "evals" / "evals.json").resolve()
    workspace_root = workspace or skill_root.parent / f"{skill_root.name}-workspace"
    iteration_root = workspace_root / iteration
    iteration_root.mkdir(parents=True, exist_ok=True)

    eval_set = _load_eval_set(evals_path)
    evals = eval_set["evals"]
    skill_digest = hashlib.sha256()
    for path in sorted(skill_root.rglob("*")):
        relative = path.relative_to(skill_root)
        if path.is_file() and (
            relative.as_posix() == "SKILL.md" or relative.parts[0] in {"assets", "references"}
        ):
            skill_digest.update(relative.as_posix().encode())
            skill_digest.update(path.read_bytes())
    run_reports: list[dict[str, Any]] = []
    _progress(
        progress,
        (
            f"Starting offline evals: {len(evals)} eval(s), agent={agent}, "
            f"workspace={iteration_root}"
        ),
    )

    for index, eval_case in enumerate(evals):
        eval_name = _eval_name(eval_case, index)
        eval_dir = iteration_root / eval_name
        run_dir = eval_dir / "with_skill"
        output_dir = run_dir / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        prompt = _build_agent_prompt(skill_root=skill_root, eval_case=eval_case)
        metadata = {
            "eval_id": eval_case.get("id", index),
            "eval_name": eval_name,
            "source": eval_case.get("source"),
            "category": eval_case.get("category"),
            "source_materials": eval_case.get("source_materials", []),
            "prompt": eval_case["prompt"],
            "expected_output": eval_case.get("expected_output"),
            "assertions": eval_case.get("assertions", []),
            "agent": agent,
            "model": model,
            "skill_sha256": skill_digest.hexdigest(),
            "dry_run": dry_run,
            "offline": True,
        }

        if not rerun_passed:
            skipped_report = _passed_existing_run_report(
                run_dir=run_dir,
                metadata=metadata,
                eval_name=eval_name,
                progress=progress,
                progress_label=f"[{index + 1}/{len(evals)}] {eval_name}",
            )
            if skipped_report is not None:
                run_reports.append(skipped_report)
                continue

        _write_json(eval_dir / "eval_metadata.json", metadata)
        (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

        _progress(
            progress,
            (
                f"[{index + 1}/{len(evals)}] {eval_name}: "
                f"starting agent={agent}, timeout={timeout_seconds}s"
            ),
        )
        started = time.monotonic()
        if dry_run:
            output = "DRY RUN: agent was not invoked.\n"
            returncode = 0
            command = ["dry-run"]
        elif agent == "mock":
            output = _mock_output(eval_case)
            returncode = 0
            command = ["mock"]
        else:
            command = _agent_command(agent=agent, prompt=prompt, skill_root=skill_root, model=model)
            try:
                output, returncode = _run_agent_command(
                    command=command,
                    cwd=skill_root,
                    timeout=timeout_seconds,
                    progress=progress,
                    progress_label=f"[{index + 1}/{len(evals)}] {eval_name}",
                    progress_interval_seconds=progress_interval_seconds,
                )
            except subprocess.TimeoutExpired:
                _progress(progress, f"[{index + 1}/{len(evals)}] {eval_name}: timed out")
                output = (
                    f"Agent command timed out after {timeout_seconds} seconds.\n"
                    f"Command: {_format_command(command)}\n"
                )
                returncode = -1
        duration_seconds = round(time.monotonic() - started, 3)

        (output_dir / "response.md").write_text(output, encoding="utf-8")
        timing = {
            "duration_seconds": duration_seconds,
            "returncode": returncode,
            "command": command,
        }
        _write_json(run_dir / "timing.json", timing)

        grading = _grade_output(
            output=output,
            assertions=_string_list(eval_case.get("assertions")),
            returncode=returncode,
            dry_run=dry_run,
        )
        _write_json(run_dir / "grading.json", grading)
        status = "pass" if grading["passed"] else "fail"
        _progress(
            progress,
            (
                f"[{index + 1}/{len(evals)}] {eval_name}: {status} "
                f"({grading['passed_assertions']}/{grading['total_assertions']} assertions, "
                f"{duration_seconds}s, returncode={returncode})"
            ),
        )
        run_reports.append(
            {
                "eval_id": metadata["eval_id"],
                "eval_name": eval_name,
                "source": metadata["source"],
                "category": metadata["category"],
                "source_materials": metadata["source_materials"],
                "run_dir": str(run_dir),
                "passed": grading["passed"],
                "passed_assertions": grading["passed_assertions"],
                "total_assertions": grading["total_assertions"],
                "duration_seconds": duration_seconds,
                "returncode": returncode,
            }
        )

    report = {
        "skill_root": str(skill_root),
        "evals_path": str(evals_path),
        "workspace": str(iteration_root),
        "agent": agent,
        "model": model,
        "dry_run": dry_run,
        "summary": {
            "eval_count": len(run_reports),
            "passed": sum(1 for item in run_reports if item["passed"]),
            "failed": sum(1 for item in run_reports if not item["passed"]),
            "skipped": sum(1 for item in run_reports if item.get("skipped")),
            "by_source": _summarize_by_field(run_reports, "source"),
            "by_category": _summarize_by_field(run_reports, "category"),
        },
        "runs": run_reports,
    }
    _write_json(iteration_root / "summary.json", report)
    (iteration_root / "summary.md").write_text(_render_summary_markdown(report), encoding="utf-8")
    _progress(
        progress,
        (
            f"Finished offline evals: {report['summary']['passed']} passed, "
            f"{report['summary']['failed']} failed, "
            f"{report['summary']['skipped']} skipped. Summary: {iteration_root / 'summary.md'}"
        ),
    )
    return report


def _progress(enabled: bool, message: str) -> None:
    if enabled:
        print(message, flush=True)


def _passed_existing_run_report(
    *,
    run_dir: Path,
    metadata: dict[str, Any],
    eval_name: str,
    progress: bool,
    progress_label: str,
) -> dict[str, Any] | None:
    grading_path = run_dir / "grading.json"
    timing_path = run_dir / "timing.json"
    if not grading_path.exists():
        return None
    previous_metadata = _load_optional_json_object(run_dir.parent / "eval_metadata.json")
    if previous_metadata != metadata:
        _progress(progress, f"{progress_label}: inputs or model changed; rerunning")
        return None
    try:
        grading = json.loads(grading_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        _progress(progress, f"{progress_label}: existing grading.json is invalid; rerunning")
        return None
    if not isinstance(grading, dict) or grading.get("passed") is not True:
        return None

    timing = _load_optional_json_object(timing_path)
    duration_seconds = timing.get("duration_seconds", 0) if timing is not None else 0
    returncode = timing.get("returncode", 0) if timing is not None else 0
    passed_assertions = grading.get("passed_assertions", 0)
    total_assertions = grading.get("total_assertions", 0)
    _progress(
        progress,
        (
            f"{progress_label}: skipped existing pass "
            f"({passed_assertions}/{total_assertions} assertions)"
        ),
    )
    return {
        "eval_id": metadata["eval_id"],
        "eval_name": eval_name,
        "source": metadata["source"],
        "category": metadata["category"],
        "source_materials": metadata["source_materials"],
        "run_dir": str(run_dir),
        "passed": True,
        "passed_assertions": passed_assertions,
        "total_assertions": total_assertions,
        "duration_seconds": duration_seconds,
        "returncode": returncode,
        "skipped": True,
    }


def _load_optional_json_object(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _format_command(command: list[str]) -> str:
    parts = []
    for part in command:
        cleaned = part.replace("\n", "\\n")
        if len(cleaned) > 160:
            cleaned = f"{cleaned[:157]}..."
        parts.append(cleaned)
    return " ".join(parts)


def _load_eval_set(evals_path: Path) -> dict[str, Any]:
    payload = json.loads(evals_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("evals.json must parse to an object")
    evals = payload.get("evals")
    if not isinstance(evals, list) or not evals:
        raise ValueError("evals.json must include a non-empty evals list")
    for index, eval_case in enumerate(evals):
        if not isinstance(eval_case, dict):
            raise ValueError(f"evals[{index}] must be an object")
        prompt = eval_case.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(f"evals[{index}].prompt must be a non-empty string")
    return payload


def _summarize_by_field(
    run_reports: list[dict[str, Any]],
    field: str,
) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for report in run_reports:
        raw_key = report.get(field)
        key = raw_key if isinstance(raw_key, str) and raw_key.strip() else "unspecified"
        bucket = summary.setdefault(key, {"eval_count": 0, "passed": 0, "failed": 0})
        bucket["eval_count"] += 1
        if report["passed"]:
            bucket["passed"] += 1
        else:
            bucket["failed"] += 1
    return summary


def _build_agent_prompt(*, skill_root: Path, eval_case: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Execute this offline expert-skill eval.",
            "",
            f"- Skill path: {skill_root}",
            "- Runtime mode: offline dry planning only.",
            "- Do not call nextflow_run to launch work.",
            "- Do not run Nextflow.",
            "- Write the entire eval response in English, even if repository instructions or the "
            "task prompt use another language.",
            "- Return a structured plan or YAML-like summary.",
            "",
            "Task prompt:",
            eval_case["prompt"],
            "",
        ]
    )


def _agent_command(
    *, agent: str, prompt: str, skill_root: Path, model: str | None = None
) -> list[str]:
    working_root = skill_root
    if agent == "claude":
        return [
            "claude",
            "--print",
            "--permission-mode",
            "dontAsk",
            "--add-dir",
            str(working_root),
            prompt,
        ]
    if agent == "codex":
        return [
            "codex",
            "--ask-for-approval",
            "never",
            "exec",
            "--cd",
            str(working_root),
            "--sandbox",
            "read-only",
            "--skip-git-repo-check",
            "--ephemeral",
            *(["--model", model] if model is not None else []),
            prompt,
        ]
    if agent == "kimi":
        return [
            "kimi",
            "--work-dir",
            str(working_root),
            "--add-dir",
            str(working_root),
            "--skills-dir",
            str(skill_root.parent),
            "--quiet",
            "--prompt",
            prompt,
        ]
    raise ValueError(f"Unsupported executable agent {agent!r}")


def _run_agent_command(
    *,
    command: list[str],
    cwd: Path,
    timeout: int,
    progress: bool,
    progress_label: str,
    progress_interval_seconds: int,
) -> tuple[str, int]:
    progress_interval_seconds = max(1, progress_interval_seconds)
    started = time.monotonic()
    deadline = started + timeout
    next_progress_at = started + progress_interval_seconds
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as stdout_file:
        with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as stderr_file:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                text=True,
                stdout=stdout_file,
                stderr=stderr_file,
            )
            while True:
                returncode = process.poll()
                now = time.monotonic()
                if returncode is not None:
                    break
                if now >= deadline:
                    process.kill()
                    process.wait()
                    raise subprocess.TimeoutExpired(command, timeout)
                if progress and now >= next_progress_at:
                    elapsed = int(now - started)
                    remaining = max(0, int(deadline - now))
                    print(
                        f"{progress_label}: still running ({elapsed}s elapsed, "
                        f"{remaining}s before timeout)",
                        flush=True,
                    )
                    next_progress_at = now + progress_interval_seconds
                time.sleep(min(1.0, max(0.1, next_progress_at - now)))

            stdout_file.seek(0)
            stderr_file.seek(0)
            stdout = stdout_file.read()
            stderr = stderr_file.read()

    if stderr:
        stdout = f"{stdout}\n\n[stderr]\n{stderr}".strip() + "\n"
    return stdout, returncode


def _mock_output(eval_case: dict[str, Any]) -> str:
    del eval_case
    lines = [
        "# Mock Offline Eval Output",
        "",
        "This output is generated by --agent mock for runner testing.",
        "",
        "tool_order:",
        "  - project_get",
        "  - nextflow_run(prepare=true) when launch uncertainty remains",
        "  - nextflow_run",
        '  - run_get(include=["progress","artifact_summary","diagnosis","next_actions"])',
        "  - run_artifacts",
        "  - fs_read after an explicit path is known",
        "  - run_logs only after summary checks if raw logs are still needed",
        "",
        "nextflow_run_shape:",
        "  project: top_level",
        "  params:",
        "    input: <server_input_root>/samplesheet.csv",
        "    outdir: <server_output_root>/pipeline",
        "    ancient_dna: true",
        "    binning_map_mode: own",
        "  config_files:",
        "    - <server_input_root>/resource_override.config",
        "",
        "route_selection:",
        "  playbook: hybrid_assembly",
        "  preset: hybrid_assembly",
        "  schema_lookup:",
        "    - schema-index.yaml",
        "    - schema group for route-shaping parameters",
        "  checks:",
        "    - skip_spadeshybrid=false",
        "    - skip_flye=false",
        "    - skip_metamdbg=false",
        "",
        "historical_reuse:",
        "  - run_list(project=..., pipeline=..., artifact_path_contains=...)",
        '  - run_get(include=["artifact_summary"])',
        "  - run_artifacts",
        "  - artifacts.json",
        "  - pipeline_fingerprint",
        "  - pipeline_info/params.json compatibility check",
        "",
        "coverage_review:",
        "  - authoring-gaps.yaml",
        "  - scoped out with a reason when packaged assets do not support the request",
        "  - do not pretend unresolved gaps are complete",
        "",
        "notes:",
        "  - do not invent unsupported enum values or parameter names",
        "  - do not guess old output directories as the default safe path",
    ]
    return "\n".join(lines) + "\n"


def _grade_output(
    *,
    output: str,
    assertions: list[str],
    returncode: int,
    dry_run: bool,
) -> dict[str, Any]:
    expectations: list[dict[str, Any]] = []
    if returncode != 0:
        expectations.append(
            {
                "text": "Agent command exits successfully.",
                "passed": False,
                "evidence": f"returncode={returncode}",
            }
        )

    for assertion in assertions:
        passed, evidence = _grade_assertion(output=output, assertion=assertion, dry_run=dry_run)
        expectations.append(
            {
                "text": assertion,
                "passed": passed,
                "evidence": evidence,
            }
        )

    passed_count = sum(1 for item in expectations if item["passed"])
    return {
        "passed": bool(expectations) and passed_count == len(expectations),
        "passed_assertions": passed_count,
        "total_assertions": len(expectations),
        "expectations": expectations,
    }


def _grade_assertion(*, output: str, assertion: str, dry_run: bool) -> tuple[bool, str]:
    if dry_run:
        return False, "Dry run did not invoke an agent."
    lowered_output = output.lower()
    lowered_assertion = assertion.lower()

    if "does not use nextflow_inspect_pipeline" in lowered_assertion:
        return (
            not _has_positive_forbidden_tool_use(output, "nextflow_inspect_pipeline"),
            "Checked forbidden inspect tool.",
        )
    if "does not jump straight to raw logs" in lowered_assertion:
        return (
            _uses_summary_before_logs(lowered_output),
            "Checked summary first.",
        )
    if "does not guess" in lowered_assertion:
        guessed = _has_positive_forbidden_term(output, "guess")
        return not guessed, "Checked output for path guessing language."
    if "project as a top-level" in lowered_assertion:
        return "project" in lowered_output and "params" in lowered_output, "Checked project/params."
    if "input and outdir under params" in lowered_assertion:
        return (
            "input" in lowered_output and "outdir" in lowered_output and "params" in lowered_output,
            "Checked params fields.",
        )
    if "resource caps under config_files" in lowered_assertion:
        return (
            "config_files" in lowered_output or "override config" in lowered_output,
            "Checked config_files.",
        )
    if "run_get" in lowered_assertion:
        return "run_get" in lowered_output, "Checked run_get mention."
    if "run_artifacts" in lowered_assertion:
        return "run_artifacts" in lowered_output, "Checked run_artifacts mention."
    if "fs_read" in lowered_assertion:
        return "fs_read" in lowered_output, "Checked fs_read mention."
    if "run_list" in lowered_assertion:
        return "run_list" in lowered_output, "Checked run_list mention."
    if "artifact_path_contains" in lowered_assertion:
        return "artifact_path_contains" in lowered_output, "Checked artifact_path_contains."
    if "artifacts.json" in lowered_assertion or "pipeline_fingerprint" in lowered_assertion:
        return (
            "artifacts.json" in lowered_output or "pipeline_fingerprint" in lowered_output,
            "Checked historical artifact facts.",
        )
    if "schema-index" in lowered_assertion or "grouped schema" in lowered_assertion:
        if _scopes_out_unsupported_request(lowered_output):
            return True, "Scoped out unsupported request; schema lookup not required."
        return (
            "schema-index" in lowered_output
            or "schema group" in lowered_output
            or "schema-groups" in lowered_output,
            "Checked schema lookup mention.",
        )
    if "playbook" in lowered_assertion or "preset" in lowered_assertion:
        return "playbook" in lowered_output or "preset" in lowered_output, "Checked route assets."
    if "authoring-gaps.yaml" in lowered_assertion or "unresolved gap" in lowered_assertion:
        return (
            "authoring-gaps.yaml" in lowered_output or "unresolved gap" in lowered_output,
            "Checked authoring gap mention.",
        )
    if "scopes out" in lowered_assertion or "scoped out" in lowered_assertion:
        return "scoped out" in lowered_output or "scope" in lowered_output, "Checked scope-out."
    if "does not invent" in lowered_assertion:
        return (
            not _has_positive_forbidden_term(output, "invent"),
            "Weak check.",
        )

    keywords = _keywords_from_assertion(assertion)
    matched = [keyword for keyword in keywords if keyword in lowered_output]
    required = min(len(keywords), 2)
    return len(matched) >= required, f"Matched keywords: {matched}"


def _has_positive_forbidden_tool_use(output: str, tool_name: str) -> bool:
    """Return True when a forbidden tool is recommended, not merely denied."""
    previous_context = ""
    for line in output.splitlines():
        lowered_line = line.lower()
        if lowered_line.strip():
            current_context = lowered_line
        else:
            current_context = previous_context
        if tool_name.lower() not in lowered_line:
            previous_context = current_context
            continue
        if _line_negates_phrase(lowered_line, tool_name.lower()) or _forbidden_list_context(
            previous_context
        ):
            previous_context = current_context
            continue
        return True
    return False


def _has_positive_forbidden_term(output: str, term: str) -> bool:
    """Return True when a forbidden term appears outside a negated safety rule."""
    pattern = re.compile(rf"\b{re.escape(term.lower())}\w*\b")
    for line in output.splitlines():
        lowered_line = line.lower()
        if not pattern.search(lowered_line):
            continue
        if _line_negates_phrase(lowered_line, term.lower()):
            continue
        return True
    return False


def _line_negates_phrase(line: str, phrase: str) -> bool:
    """Recognize common safety phrasing near a forbidden phrase."""
    phrase_index = line.find(phrase)
    if phrase_index < 0:
        return False
    prefix = line[max(0, phrase_index - 80) : phrase_index]
    return any(
        marker in prefix
        for marker in (
            "do not ",
            "don't ",
            "does not ",
            "never ",
            "avoid ",
            "without ",
            "no ",
            "not ",
            "should not ",
            "must not ",
            "forbid",
            "forbidden",
            "instead of ",
        )
    )


def _forbidden_list_context(line: str) -> bool:
    return any(
        marker in line
        for marker in (
            "forbidden",
            "do not",
            "not use",
            "not call",
            "must not",
            "avoid",
        )
    )


def _uses_summary_before_logs(lowered_output: str) -> bool:
    """Check that the response starts from run summaries or avoids logs by default."""
    if "run_get" not in lowered_output:
        return False
    log_positions = [
        position
        for token in ("run_logs", "raw logs", "nextflow log")
        if (position := lowered_output.find(token)) >= 0
    ]
    if not log_positions:
        return True
    first_log = min(log_positions)
    first_summary = lowered_output.find("run_get")
    if first_summary < first_log:
        return True
    log_context = lowered_output[max(0, first_log - 100) : first_log + 100]
    return any(
        marker in log_context
        for marker in (
            "before raw logs",
            "after summary",
            "after run_get",
            "only after",
            "not jump",
            "do not jump",
        )
    )


def _scopes_out_unsupported_request(lowered_output: str) -> bool:
    scope_markers = ("scoped out", "scope out", "scope_out_reason", "not supported")
    unsupported_markers = (
        "no parameter",
        "no standalone",
        "not a standalone",
        "not as an input prerequisite",
        "no runtime planning action",
        "no playbook",
        "no preset",
        "zero matches",
    )
    return any(marker in lowered_output for marker in scope_markers) and any(
        marker in lowered_output for marker in unsupported_markers
    )


def _keywords_from_assertion(assertion: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{2,}", assertion.lower())
    stopwords = {
        "the",
        "and",
        "for",
        "with",
        "when",
        "that",
        "this",
        "does",
        "not",
        "uses",
        "use",
        "mentions",
        "starts",
        "requires",
    }
    return [token for token in tokens if token not in stopwords]


def _eval_name(eval_case: dict[str, Any], index: int) -> str:
    raw = eval_case.get("id", f"eval-{index}")
    if not isinstance(raw, str) or not raw.strip():
        raw = f"eval-{index}"
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "-", raw.strip()).strip("-")
    return slug or f"eval-{index}"


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def _render_summary_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Offline Eval Summary",
        "",
        f"- Skill root: `{report['skill_root']}`",
        f"- Agent: `{report['agent']}`",
        f"- Requested model: `{report.get('model') or 'client default'}`",
        f"- Dry run: `{report['dry_run']}`",
        f"- Passed: {report['summary']['passed']}",
        f"- Failed: {report['summary']['failed']}",
        f"- Skipped existing passes: {report['summary'].get('skipped', 0)}",
    ]
    lines.extend(["", "## By Source", ""])
    for source, counts in report["summary"]["by_source"].items():
        lines.append(
            f"- `{source}`: {counts['passed']} passed, {counts['failed']} failed "
            f"({counts['eval_count']} evals)"
        )
    lines.extend(["", "## By Category", ""])
    for category, counts in report["summary"]["by_category"].items():
        lines.append(
            f"- `{category}`: {counts['passed']} passed, {counts['failed']} failed "
            f"({counts['eval_count']} evals)"
        )
    lines.extend(["", "## Runs", ""])
    for run in report["runs"]:
        status = "skip" if run.get("skipped") else "pass" if run["passed"] else "fail"
        source = run["source"] or "unspecified"
        category = run["category"] or "unspecified"
        lines.append(
            f"- `{run['eval_name']}` [{source}/{category}]: {status} "
            f"({run['passed_assertions']}/{run['total_assertions']} assertions)"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run offline evals.json prompts for a generated pipeline expert skill."
    )
    parser.add_argument("--skill-root", required=True, help="Path to a <pipeline>-expert-skill.")
    parser.add_argument(
        "--evals", help="Path to evals.json. Defaults to <skill-root>/evals/evals.json."
    )
    parser.add_argument("--workspace", help="Workspace root. Defaults beside the skill directory.")
    parser.add_argument("--iteration", default="iteration-1", help="Iteration directory name.")
    parser.add_argument(
        "--agent",
        default=DEFAULT_AGENT,
        choices=sorted(SUPPORTED_AGENTS),
        help="Agent CLI to invoke. Use mock for runner tests.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument(
        "--model", help="Explicit Codex model ID; unavailable models fail without fallback."
    )
    parser.add_argument(
        "--progress-interval-seconds",
        type=int,
        default=DEFAULT_PROGRESS_INTERVAL_SECONDS,
        help="Seconds between still-running progress messages while an agent call is active.",
    )
    parser.add_argument(
        "--quiet-progress",
        action="store_true",
        help="Disable progress messages and print only the final summary.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Create metadata and failing grading placeholders without invoking an agent.",
    )
    parser.add_argument(
        "--rerun-passed",
        action="store_true",
        help="Rerun evals even when an existing grading.json already passed.",
    )
    args = parser.parse_args()

    report = run_offline_evals(
        skill_root=Path(args.skill_root),
        evals_path=Path(args.evals) if args.evals else None,
        workspace=Path(args.workspace) if args.workspace else None,
        iteration=args.iteration,
        agent=args.agent,
        timeout_seconds=args.timeout_seconds,
        dry_run=args.dry_run,
        model=args.model,
        rerun_passed=args.rerun_passed,
        progress=not args.quiet_progress,
        progress_interval_seconds=args.progress_interval_seconds,
    )
    print(yaml.safe_dump(report["summary"], sort_keys=False), end="")
    return 0 if report["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
