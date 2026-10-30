"""Local process runner for detached jobs."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

from nextmcp.process_runtime import (
    DEFAULT_STOP_GRACE_SECONDS,
    get_job_paths,
    read_json,
    write_json,
)


def main(argv: list[str] | None = None) -> None:
    """Run a single job directory command."""
    parser = argparse.ArgumentParser(description="nextmcp process runner")
    parser.add_argument("job_dir", help="Path to the process job directory")
    args = parser.parse_args(argv)

    job_paths = get_job_paths(Path(args.job_dir))
    command = _require_command(read_json(job_paths.command_json))

    env = os.environ.copy()
    env.update(_require_env(command.get("env")))

    with job_paths.stdout_log.open("a", encoding="utf-8") as stdout_handle:
        with job_paths.stderr_log.open("a", encoding="utf-8") as stderr_handle:
            proc = subprocess.Popen(
                _require_argv(command.get("argv")),
                cwd=str(command["cwd"]),
                env=env,
                stdin=subprocess.PIPE if command.get("stdin") is not None else subprocess.DEVNULL,
                stdout=stdout_handle,
                stderr=stderr_handle,
                text=True,
                start_new_session=True,
            )

            write_json(
                job_paths.runtime_json,
                {
                    "pid": proc.pid,
                    "pgid": os.getpgid(proc.pid),
                    "started_at": _utcnow(),
                },
            )

            stdin_value = command.get("stdin")
            if stdin_value is not None and proc.stdin is not None:
                proc.stdin.write(str(stdin_value))
                proc.stdin.close()

            timeout_seconds = _optional_float(command.get("timeout_seconds"))
            timed_out = False
            try:
                exit_code = proc.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                timed_out = True
                _terminate_for_timeout(proc.pid)
                exit_code = proc.wait()

    stop_requested = job_paths.stop_json.exists()
    status = _status_from_exit(exit_code, stop_requested=stop_requested, timed_out=timed_out)
    write_json(
        job_paths.result_json,
        {
            "status": status,
            "exit_code": exit_code,
            "finished_at": _utcnow(),
            "timed_out": timed_out,
        },
    )


def _terminate_for_timeout(pid: int) -> None:
    """Terminate a timed-out process group."""
    pgid = os.getpgid(pid)
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return

    deadline = time.monotonic() + DEFAULT_STOP_GRACE_SECONDS
    while time.monotonic() < deadline:
        try:
            os.killpg(pgid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.1)

    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        return


def _status_from_exit(
    exit_code: int,
    *,
    stop_requested: bool,
    timed_out: bool,
) -> str:
    """Map a subprocess exit code to public status."""
    if stop_requested:
        return "stopped"
    if timed_out:
        return "failed"
    if exit_code == 0:
        return "succeeded"
    return "failed"


def _require_command(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Require command.json content to exist."""
    if payload is None:
        raise FileNotFoundError("Missing command.json")
    return payload


def _require_argv(value: Any) -> list[str]:
    """Validate argv payload from command.json."""
    if not isinstance(value, list) or not value:
        raise ValueError("command argv must be a non-empty list")
    return [str(item) for item in value]


def _require_env(value: Any) -> dict[str, str]:
    """Validate env payload from command.json."""
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("command env must be a dict")
    return {str(key): str(item) for key, item in value.items()}


def _optional_float(value: Any) -> float | None:
    """Convert an optional JSON value to float."""
    if value is None:
        return None
    return float(value)


def _utcnow() -> str:
    """Return an ISO8601 UTC timestamp."""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


if __name__ == "__main__":
    main()
