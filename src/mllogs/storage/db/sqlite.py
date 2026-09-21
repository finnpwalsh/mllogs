from pathlib import Path
import sqlite3
import json
from datetime import datetime

from .base import DBStore
from mllogs.run import Run, RunStatus


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
                name        TEXT,
                run_type    TEXT,
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


    def save_run(self, run: Run) -> None:
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO runs (
                    id,
                    started_at,
                    status,
                    name,
                    run_type,
                    ended_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    run.id,
                    run.started_at.isoformat(),
                    run.status.value,
                    run.name,
                    run.run_type,
                    run.ended_at.isoformat() if run.ended_at else None,
                ),
            )

            self._connection.executemany(
                """
                INSERT INTO params (run_id, key, value)
                VALUES (?, ?, ?)
                """,
                [
                    (run.id, key, json.dumps(value))
                    for key, value in run.params.items()
                ],
            )

            self._connection.executemany(
                """
                INSERT INTO metrics (run_id, key, value)
                VALUES (?, ?, ?)
                """,
                [
                    (run.id, key, value)
                    for key, value in run.metrics.items()
                ],
            )

            self._connection.executemany(
                """
                INSERT INTO tags (run_id, key, value)
                VALUES (?, ?, ?)
                """,
                [
                    (run.id, key, str(value))
                    for key, value in run.tags.items()
                ],
            )


    def load_run(self, run_id: str | None = None) -> Run | None:
        if run_id is None:
            run_row = self._connection.execute(
                """
                SELECT *
                FROM runs
                ORDER BY started_at DESC
                LIMIT 1
                """
            ).fetchone()
        else:
            run_row = self._connection.execute(
                "SELECT * FROM runs WHERE id = ?",
                (run_id,),
            ).fetchone()

        if run_row is None:
            return None

        run_id = run_row["id"]
        
        param_rows = self._connection.execute(
            "SELECT key, value FROM params WHERE run_id = ?",
            (run_id,),
        ).fetchall()

        metric_rows = self._connection.execute(
            "SELECT key, value FROM metrics WHERE run_id = ?",
            (run_id,),
        ).fetchall()

        tag_rows = self._connection.execute(
            "SELECT key, value FROM tags WHERE run_id = ?",
            (run_id,),
        ).fetchall()

        return Run(
            id=run_row["id"],
            started_at=datetime.fromisoformat(run_row["started_at"]),
            status=RunStatus(run_row["status"]),
            name=run_row["name"],
            run_type=run_row["run_type"],
            ended_at=(
                datetime.fromisoformat(run_row["ended_at"])
                if run_row["ended_at"]
                else None
            ),
            params={
                row["key"]: json.loads(row["value"])
                for row in param_rows
            },
            metrics={
                row["key"]: row["value"]
                for row in metric_rows
            },
            tags={
                row["key"]: row["value"]
                for row in tag_rows
            },
        )


    def list_runs(self, limit: int | None = None) -> list[Run]:
        if limit is not None and limit <= 0:
            raise ValueError("limit must be greater than 0")

        query = """
            SELECT id
            FROM runs
            ORDER BY started_at DESC
        """

        params = ()

        if limit is not None:
            query += " LIMIT ?"
            params = (limit, )

        rows = self._connection.execute(
            query,
            params,
        ).fetchall()

        return [
            self.load_run(row["id"])
            for row in rows
        ]


    def delete_run(self, run_id: str) -> None:
        with self._connection:
            cursor = self._connection.execute(
                "DELETE FROM runs WHERE id = ?",
                (run_id,),
            )

        if cursor.rowcount == 0:
            raise KeyError(f"Run not found: {run_id}")