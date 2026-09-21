from pathlib import Path
import sqlite3
import json
from datetime import datetime

from .base import DBStore
from mllogs.run import Run, RunStatus
from mllogs.types import ParamValue


class SQLiteStore(DBStore):
    def __init__(self, db_path: str | Path = ".mllogs/mllogs.db") -> None:
        self._db_path = Path(db_path)

        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        self._connection = sqlite3.connect(self._db_path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")

        self._initialize_schema()


    def _initialize_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id          TEXT PRIMARY KEY,
                started_at  TEXT NOT NULL,
                status      TEXT NOT NULL,
                ended_at    TEXT
            );

            CREATE TABLE IF NOT EXISTS params (
                run_id      TEXT NOT NULL,
                key         TEXT NOT NULL,
                value       TEXT NOT NULL,

                PRIMARY KEY (run_id, key),
                FOREIGN KEY (run_id)
                    REFERENCES runs(id)
                    ON DELETE CASCADE
            
            );

            CREATE TABLE IF NOT EXISTS metrics (
                run_id          TEXT NOT NULL,
                key             TEXT NOT NULL,
                value           REAL NOT NULL,

                PRIMARY KEY (run_id, key),
                FOREIGN KEY (run_id)
                    REFERENCES runs(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS tags (
                run_id          TEXT NOT NULL,
                key             TEXT NOT NULL,
                value           TEXT NOT NULL,

                PRIMARY KEY (run_id, key),
                FOREIGN KEY (run_id)
                    REFERENCES runs(id)
                    ON DELETE CASCADE
            );
            """     
        )

    def _require_run(self, run_id: str) -> None:
        row = self._connection.execute(
            "SELECT 1 FROM runs WHERE id = ?",
            (run_id,),
        ).fetchone()

        if row is None:
            raise KeyError(f"Run not found: {run_id}")

    # =================
    # ----- Write -----
    # =================

    def save_run(self, run: Run) -> None:
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO runs (
                    id,
                    started_at,
                    status,
                    ended_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    run.id,
                    run.started_at.isoformat(),
                    run.status.value,
                    run.ended_at.isoformat() if run.ended_at else None,
                ),
            )


    def update_run(self, run: Run) -> None:
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE runs
                SET
                    status = ?,
                    ended_at = ?
                WHERE id = ?
                """,
                (
                    run.status.value,
                    run.ended_at.isoformat() if run.ended_at else None,
                    run.id,
                ),
            )

            if cursor.rowcount == 0:
                raise KeyError(f"Run not found: {run.id}")


    def save_param(
        self,
        run_id: str,
        key: str,
        value: ParamValue,
    ) -> None:
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO params (
                    run_id,
                    key,
                    value
                )
                VALUES (?, ?, ?)
                """,
                (
                    run_id,
                    key,
                    json.dumps(value),
                ),
            )


    def save_metric(
        self,
        run_id: str,
        key: str,
        value: float,
    ) -> None:
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO metrics (
                    run_id,
                    key,
                    value
                )
                VALUES (?, ?, ?)
                """,
                (
                    run_id,
                    key,
                    value,
                ),
            )

    def save_tag(
        self,
        run_id: str,
        key: str,
        value: str,
    ) -> None:
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO tags (
                    run_id,
                    key,
                    value
                )
                VALUES (?, ?, ?)
                """,
                (
                    run_id,
                    key,
                    value,
                ),
            )

    # ================
    # ----- Read -----
    # ================

    def load_run(self, run_id: str) -> Run:
        run_row = self._connection.execute(
            "SELECT * FROM runs WHERE id = ?",
            (run_id,),
        ).fetchone()

        if run_row is None:
            raise KeyError(f"Run not found: {run_id}")

        return Run(
            id=run_row["id"],
            started_at=datetime.fromisoformat(run_row["started_at"]),
            status=RunStatus(run_row["status"]),
            ended_at=(
                datetime.fromisoformat(run_row["ended_at"])
                if run_row["ended_at"]
                else None
            ),
        )


    def load_params(self, run_id: str) -> dict[str, ParamValue]:
        self._require_run(run_id)

        rows = self._connection.execute(

            """
            SELECT key, value
            FROM params
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchall()

        return {
            row["key"]: json.loads(row["value"])
            for row in rows
        }


    def load_metrics(self, run_id: str) -> dict[str, float]:
        self._require_run(run_id)

        rows = self._connection.execute(

            """
            SELECT key, value
            FROM metrics
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchall()

        return {
            row["key"]: row["value"]
            for row in rows
        }


    def load_tags(self, run_id: str) -> dict[str, str]:
        self._require_run(run_id)
        
        rows = self._connection.execute(

            """
            SELECT key, value
            FROM tags
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchall()

        return {
            row["key"]: row["value"]
            for row in rows
        }

    # ==================
    # ----- Delete -----
    # ==================

    def delete_run(self, run_id: str) -> None:
        with self._connection:
            cursor = self._connection.execute(
                """
                DELETE FROM runs
                WHERE id = ?
                """,
                (run_id,),
            )

            if cursor.rowcount == 0:
                raise KeyError(f"Run not found: {run_id}")