from pathlib import Path
import sqlite3

from .base import DBStore
from mllogs.run import Run


class SQLiteStore(DBStore):
    def __init__(self, db_path: str | Path = ".mllogs/mllogs.db") -> None:
        self._db_path = Path(db_path)

        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        self._connection = sqlite3.connect(self._db_path)
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
                value           TEXT NOT NULL,

                PRIMARY KEY (run_id, key),
                FOREIGN KEY (run_id)
                    REFERENCES runs(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS tags (
                run_id          TEXT NOT NULL,
                key             TEXT NOT NULL,
                value           REAL NOT NULL,

                PRIMARY KEY (run_id, key),
                FOREIGN KEY (run_id)
                    REFERENCES runs(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS artifacts (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id          TEXT NOT NULL,
                name            TEXT NOT NULL,
                uri             TEXT NOT NULL,
                artifact_type   TEXT,

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
                    (run.id, key, str(value))
                    for key, value in run.params.items()
                ],
            )

            self._connection.executemany(
                """
                INSERT INTO metrics (run_id, key, value)
                VALUES (?, ?, ?)
                """,
                [
                    (run.id, key, str(value))
                    for key, value in run.params.items()
                ],
            )

            self._connection.executemany(
                """
                INSERT INTO tags (run_id, key, value)
                VALUES (?, ?, ?)
                """,
                [
                    (run.id, key, str(value))
                    for key, value in run.params.items()
                ],
            )

            self._connection.executemany(
                """
                INSERT INTO artifacts (
                    run_id,
                    name,
                    uri,
                    artifact_type
                )
                VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        run.id,
                        artifact.name,
                        artifact.uri,
                        artifact.artifact_type,
                    )
                    for artifact in run.artifacts
                ]
            )