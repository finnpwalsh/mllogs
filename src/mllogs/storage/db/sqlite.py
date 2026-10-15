from pathlib import Path
import sqlite3
import json
from datetime import datetime

from .base import DBStore
from mllogs.experiment import Experiment
from mllogs.run import Run, RunStatus
from mllogs.types import ParamValue
from mllogs.artifact import ArtifactRef


class SQLiteStore(DBStore):
    # ======================
    # ----- INITIALIZE -----
    # ======================

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
            CREATE TABLE IF NOT EXISTS experiments (
                id              TEXT PRIMARY KEY,
                name            TEXT NOT NULL UNIQUE,
                created_at      TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS runs (
                id              TEXT PRIMARY KEY,
                started_at      TEXT NOT NULL,
                status          TEXT NOT NULL,
                experiment_id   TEXT,
                ended_at        TEXT,

                FOREIGN KEY (experiment_id)
                    REFERENCES experiments(id)
                    ON DELETE SET NULL
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

            CREATE TABLE IF NOT EXISTS artifacts (
                id              TEXT PRIMARY KEY,
                run_id          TEXT NOT NULL,
                name            TEXT NOT NULL,
                format          TEXT NOT NULL,

                UNIQUE (run_id, name),
                
                FOREIGN KEY (run_id)
                    REFERENCES runs(id)
                    ON DELETE CASCADE
            );
            """  
        )


    # ===================
    # ----- HELPERS -----
    # ===================

    def _require_run(self, run_id: str) -> None:
        row = self._connection.execute(
            "SELECT 1 FROM runs WHERE id = ?",
            (run_id,),
        ).fetchone()

        if row is None:
            raise KeyError(f"Run not found: {run_id}")


    # =======================
    # ----- EXPERIMENTS -----
    # =======================
    
    def save_experiment(self, experiment: Experiment) -> None:
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO experiments (
                    id,
                    name,
                    created_at
                )
                VALUES (?, ?, ?)
                """,
                (experiment.id, experiment.name, experiment.created_at.isoformat()),
            )

    def load_experiment(self, experiment_id: str) -> Experiment:
        row = self._connection.execute(
            """
            SELECT id, name, created_at
            FROM experiments
            WHERE id = ?
            """,
            (experiment_id,),
        ).fetchone()

        if row is None:
            raise KeyError(f"No experiment found for id '{experiment_id}'.")

        return Experiment(
            id=row["id"],
            name=row["name"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def load_experiment_by_name(self, name: str) -> Experiment:
        row = self._connection.execute(
            """
            SELECT id, name, created_at
            FROM experiments
            WHERE name = ?
            """,
            (name,),
        ).fetchone()

        if row is None:
            raise KeyError(f"No experiment found for name '{name}'.")

        return Experiment(
            id=row["id"],
            name=row["name"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def load_experiments(self) -> list[Experiment]:
        rows = self._connection.execute(
            """
            SELECT id, name, created_at
            FROM experiments
            ORDER BY created_at DESC
            """,
        ).fetchall()

        return [
            Experiment(
                id=row["id"],
                name=row["name"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]

    def delete_experiment(self, experiment_id: str) -> None:
        with self._connection:
            cursor = self._connection.execute(
                """
                DELETE FROM experiments
                WHERE id = ?
                """,
                (experiment_id,),
            )

            if cursor.rowcount == 0:
                raise KeyError(f"No experiment found for id '{experiment_id}'.")


    # ================
    # ----- RUNS -----
    # ================

    def save_run(self, run: Run) -> None:
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO runs (
                    id,
                    started_at,
                    status,
                    ended_at,
                    experiment_id
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    run.id,
                    run.started_at.isoformat(),
                    run.status.value,
                    run.ended_at.isoformat() if run.ended_at else None,
                    run.experiment_id if run.experiment_id else None,
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
            experiment_id=run_row["experiment_id"] if run_row["experiment_id"] else None,
        )

    def load_runs(self, experiment_id: str | None = None) -> list[Run]:
        if experiment_id is None:
            rows = self._connection.execute(
                """
                SELECT *
                FROM runs
                ORDER BY started_at DESC
                """,
            ).fetchall()

        else:
            rows = self._connection.execute(
                """
                SELECT *
                FROM runs
                WHERE experiment_id = ?
                ORDER BY started_at DESC
                """,
                (experiment_id,),
            ).fetchall()

        return [
            Run(
                id=row["id"],
                started_at=datetime.fromisoformat(row["started_at"]),
                status=RunStatus(row["status"]),
                ended_at=(
                    datetime.fromisoformat(row["ended_at"])
                    if row["ended_at"] is not None
                    else None
                ),
                experiment_id=row["experiment_id"],
            )
            for row in rows
        ]

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


    # ========================
    # ----- RUN METADATA -----
    # ========================

    def save_param(self, run_id: str, key: str, value: ParamValue) -> None:
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


    def save_metric(self, run_id: str, key: str, value: float) -> None:
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


    def save_tag(self, run_id: str, key: str, value: str) -> None:
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


    # =====================
    # ----- ARTIFACTS -----
    # =====================

    def save_artifact_ref(self, ref: ArtifactRef) -> None:
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO artifacts (id, run_id, name, format)
                VALUES (?, ?, ?, ?)
                """,
                (ref.id, ref.run_id, ref.name, ref.format),
            )

    def load_artifact_ref(self, artifact_id: str) -> ArtifactRef:
        row = self._connection.execute(
            """
            SELECT id, run_id, name, format
            FROM artifacts
            WHERE id = ?
            """,
            (artifact_id,),
        ).fetchone()

        return ArtifactRef(
            id=row["id"],
            run_id=row["run_id"],
            name=row["name"],
            format=row["format"],
        )

    def load_artifact_refs(self, run_id: str) -> list[ArtifactRef]:
        self._require_run(run_id)

        rows = self._connection.execute(
            """
            SELECT id, run_id, name, format
            FROM artifacts
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchall()

        return [
            ArtifactRef(
                id=row["id"],
                run_id=row["run_id"],
                name=row["name"],
                format=row["format"],
            )
            for row in rows
        ]

    def load_artifact_ref_by_name(self, run_id: str, name: str) -> ArtifactRef:
        self._require_run(run_id)

        row = self._connection.execute(
            """
            SELECT id, run_id, name, format
            FROM artifacts
            WHERE run_id = ?
                AND name = ?
            """,
            (run_id, name),
        ).fetchone()

        return ArtifactRef(
            id=row["id"],
            run_id=row["run_id"],
            name=row["name"],
            format=row["format"],
        )