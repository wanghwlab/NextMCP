"""SQLite-backed process metadata store."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROCESS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS processes (
    process_id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    label TEXT,
    status TEXT NOT NULL,
    cwd TEXT NOT NULL,
    argv_json TEXT NOT NULL,
    job_dir TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT,
    runner_pid INTEGER,
    pid INTEGER,
    pgid INTEGER,
    exit_code INTEGER,
    timed_out INTEGER NOT NULL DEFAULT 0,
    stop_requested INTEGER NOT NULL DEFAULT 0
)
"""

ARTIFACT_ITEM_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS artifact_items (
    process_id TEXT NOT NULL,
    source_kind TEXT NOT NULL,
    label TEXT,
    path TEXT NOT NULL,
    rel_path TEXT,
    PRIMARY KEY (process_id, source_kind, path)
)
"""

ARTIFACT_ITEM_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS artifact_items_path_lookup
ON artifact_items (path, rel_path, label)
"""


@dataclass(frozen=True)
class ProcessRecord:
    """Stored metadata for a launched process."""

    process_id: str
    kind: str
    label: str | None
    status: str
    cwd: str
    argv: list[str]
    job_dir: str
    created_at: str
    updated_at: str
    started_at: str | None
    finished_at: str | None
    runner_pid: int | None
    pid: int | None
    pgid: int | None
    exit_code: int | None
    timed_out: bool
    stop_requested: bool


class ProcessStore:
    """Small SQLite store for process metadata."""

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(PROCESS_TABLE_SQL)
            conn.execute(ARTIFACT_ITEM_TABLE_SQL)
            conn.execute(ARTIFACT_ITEM_INDEX_SQL)
            conn.commit()

    def create_process(
        self,
        *,
        process_id: str,
        kind: str,
        label: str | None,
        cwd: str,
        argv: list[str],
        job_dir: str,
        created_at: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO processes (
                    process_id,
                    kind,
                    label,
                    status,
                    cwd,
                    argv_json,
                    job_dir,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    process_id,
                    kind,
                    label,
                    "running",
                    cwd,
                    json.dumps(argv),
                    job_dir,
                    created_at,
                    created_at,
                ),
            )
            conn.commit()

    def set_runner_pid(self, process_id: str, runner_pid: int, updated_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE processes
                SET runner_pid = ?, updated_at = ?
                WHERE process_id = ?
                """,
                (runner_pid, updated_at, process_id),
            )
            conn.commit()

    def set_runtime(
        self,
        process_id: str,
        *,
        pid: int | None,
        pgid: int | None,
        started_at: str | None,
        updated_at: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE processes
                SET pid = ?,
                    pgid = ?,
                    started_at = COALESCE(started_at, ?),
                    updated_at = ?
                WHERE process_id = ?
                """,
                (pid, pgid, started_at, updated_at, process_id),
            )
            conn.commit()

    def set_result(
        self,
        process_id: str,
        *,
        status: str,
        exit_code: int | None,
        finished_at: str,
        timed_out: bool,
        updated_at: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE processes
                SET status = ?,
                    exit_code = ?,
                    finished_at = ?,
                    timed_out = ?,
                    updated_at = ?
                WHERE process_id = ?
                """,
                (
                    status,
                    exit_code,
                    finished_at,
                    int(timed_out),
                    updated_at,
                    process_id,
                ),
            )
            conn.commit()

    def mark_stop_requested(self, process_id: str, updated_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE processes
                SET stop_requested = 1, updated_at = ?
                WHERE process_id = ?
                """,
                (updated_at, process_id),
            )
            conn.commit()

    def get_process(self, process_id: str) -> ProcessRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM processes WHERE process_id = ?",
                (process_id,),
            ).fetchone()
        if row is None:
            return None
        return _row_to_record(row)

    def delete_process(self, process_id: str) -> None:
        """Delete one stored process record."""
        with self._connect() as conn:
            conn.execute("DELETE FROM artifact_items WHERE process_id = ?", (process_id,))
            conn.execute("DELETE FROM processes WHERE process_id = ?", (process_id,))
            conn.commit()

    def list_processes(self) -> list[ProcessRecord]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM processes ORDER BY created_at DESC").fetchall()
        return [_row_to_record(row) for row in rows]

    def replace_artifact_items(
        self,
        process_id: str,
        *,
        published_roots: list[dict[str, Any]],
        items: list[dict[str, Any]],
    ) -> None:
        """Replace the stored artifact-path index for one process."""
        rows: list[tuple[str, str, str | None, str, str | None]] = [
            (
                process_id,
                "published_root",
                _optional_str(item.get("label")),
                str(item["path"]),
                None,
            )
            for item in published_roots
            if isinstance(item.get("path"), str)
        ]
        rows.extend(
            (
                process_id,
                "item",
                _optional_str(item.get("label")),
                str(item["path"]),
                _optional_str(item.get("rel_path")),
            )
            for item in items
            if isinstance(item.get("path"), str)
        )

        with self._connect() as conn:
            conn.execute("DELETE FROM artifact_items WHERE process_id = ?", (process_id,))
            if rows:
                conn.executemany(
                    """
                    INSERT INTO artifact_items (
                        process_id,
                        source_kind,
                        label,
                        path,
                        rel_path
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    rows,
                )
            conn.commit()

    def find_process_ids_by_artifact_path_contains(self, needle: str) -> list[str]:
        """Find process IDs whose indexed artifact paths mention one path fragment."""
        like_value = f"%{needle}%"
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT DISTINCT process_id
                FROM artifact_items
                WHERE path LIKE ? OR rel_path LIKE ? OR label LIKE ?
                ORDER BY process_id
                """,
                (like_value, like_value, like_value),
            ).fetchall()
        return [str(row["process_id"]) for row in rows]


def _row_to_record(row: sqlite3.Row) -> ProcessRecord:
    """Convert a SQLite row into a typed record."""
    return ProcessRecord(
        process_id=str(row["process_id"]),
        kind=str(row["kind"]),
        label=str(row["label"]) if row["label"] is not None else None,
        status=str(row["status"]),
        cwd=str(row["cwd"]),
        argv=_parse_argv(row["argv_json"]),
        job_dir=str(row["job_dir"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
        started_at=str(row["started_at"]) if row["started_at"] is not None else None,
        finished_at=str(row["finished_at"]) if row["finished_at"] is not None else None,
        runner_pid=int(row["runner_pid"]) if row["runner_pid"] is not None else None,
        pid=int(row["pid"]) if row["pid"] is not None else None,
        pgid=int(row["pgid"]) if row["pgid"] is not None else None,
        exit_code=int(row["exit_code"]) if row["exit_code"] is not None else None,
        timed_out=bool(row["timed_out"]),
        stop_requested=bool(row["stop_requested"]),
    )


def _parse_argv(raw: Any) -> list[str]:
    """Parse stored argv JSON."""
    value = json.loads(str(raw))
    if not isinstance(value, list):
        raise ValueError("Stored argv_json is not a list")
    return [str(item) for item in value]


def _optional_str(value: Any) -> str | None:
    """Convert an optional value to str."""
    if value is None:
        return None
    return str(value)
