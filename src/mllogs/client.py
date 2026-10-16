from contextlib import contextmanager
from typing import Generator
from datetime import datetime, UTC
from uuid import uuid4

import pandas as pd

from sqlalchemy import insert, delete, select, update

from .storage.db import Database
from .storage.db.schema import experiments, runs, params, metrics, tags
from .storage.files import LocalFileStore
from .serializers import get_serializer
from .query import Query, RunsQuery


type ParamValue = str | int | float | bool | None


class MLLogs:
    # ======================
    # ----- Initialize -----
    # ======================

    def __init__(
        self,
        db_url: str = "sqlite:///.mllogs/mllogs.db",
        file_url: str = ".mllogs/models",
    ) -> None:
        self._db = Database(db_url)
        self._files = LocalFileStore(file_url)
        self._active_run_id: str | None = None

    def close(self) -> None:
        self._db.close()


    # ===================
    # ----- Helpers -----
    # ===================

    @staticmethod
    def _new_id() -> str:
        return str(uuid4())

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)

    def _require_active_run(self) -> str:
        if self._active_run_id is None:
            raise RuntimeError("No active run.")
        return self._active_run_id


    # =======================
    # ----- Experiments -----
    # =======================

    def create_experiment(self, name: str) -> None:
        experiment_id = self._new_id()
        created_at = self._now()

        with self._db.engine.begin() as conn:
            conn.execute(
                insert(experiments).values(
                    id=experiment_id,
                    name=name,
                    created_at=created_at,
                )
            )

    def delete_experiment(self, name: str) -> None:
        with self._db.engine.begin() as conn:
            conn.execute(
                delete(experiments).where(
                    experiments.c.name == name
                )
            )

    def experiments(self) -> pd.DataFrame:
        stmt = select(experiments).order_by(experiments.c.name)
        return pd.read_sql(stmt, self._db.engine, parse_dates=["created_at"])

    # ================
    # ----- Runs -----
    # ================

    @contextmanager
    def run(self, experiment_name: str) -> Generator[str]:
        if self._active_run_id is not None:
            raise RuntimeError("A run is already active.")

        # Find experiment
        with self._db.engine.connect() as conn:
            experiment_id = conn.execute(
                select(experiments.c.id).where(
                    experiments.c.name == experiment_name
                )
            ).scalar_one_or_none()

        if experiment_id is None:
            raise ValueError(f"Experiment not found: {experiment_name}")

        # Start run
        run_id = self._new_id()

        with self._db.engine.begin() as conn:
            conn.execute(
                insert(runs).values(
                    id=run_id,
                    experiment_id=experiment_id,
                    started_at=self._now(),
                    status="RUNNING",
                )
            )

        self._active_run_id = run_id

        try:
            yield run_id
        except BaseException:
            status = "FAILED"
            raise
        else:
            status = "COMPLETE"
        finally:
            try:
                with self._db.engine.begin() as conn:
                    conn.execute(
                        update(runs)
                        .where(runs.c.id == run_id)
                        .values(status=status, ended_at=self._now())
                    )
            finally:
                self._active_run_id = None

    def runs(self, experiment_name: str | None = None) -> RunsQuery:
        stmt = select(runs)

        if experiment_name is not None:
            stmt = stmt.join(experiments).where(
                experiments.c.name == experiment_name
            )

        return RunsQuery(self._db, stmt)

    # ========================
    # ----- Run Metadata -----
    # ========================

    def log_param(self, key: str, value: ParamValue) -> None:
        run_id = self._require_active_run()

        with self._db.engine.begin() as conn:
            conn.execute(
                insert(params).values(
                    run_id=run_id,
                    key=key,
                    value=value,
                )
            )

    def log_metric(self, key: str, value: float) -> None:
        run_id = self._require_active_run()

        with self._db.engine.begin() as conn:
            conn.execute(
                insert(metrics).values(
                    run_id=run_id,
                    key=key,
                    value=value,
                )
            )

    def set_tag(self, key: str, value: str) -> None:
        run_id = self._require_active_run()

        with self._db.engine.begin() as conn:
            conn.execute(
                insert(tags).values(
                    run_id=run_id,
                    key=key,
                    value=value,
                )
            )


    # ==================
    # ----- Models -----
    # ==================

    def save_model(self, model: object, format: str = "joblib") -> None:
        run_id = self._require_active_run()

        # Check for existing model
        with self._db.engine.connect() as conn:
            existing_format = conn.execute(
                select(runs.c.model_format)
                .where(runs.c.id == run_id)
            ).scalar_one()

        if existing_format is not None:
            raise ValueError("A model has already been saved for this run.")

        # Serialize model
        serializer = get_serializer(format)
        data = serializer.serialize(model)

        # Save file
        path = f"{run_id}.{format}"
        self._files.save(path, data)

        # Update run metadata
        try:
            with self._db.engine.begin() as conn:
                conn.execute(
                    update(runs)
                    .where(runs.c.id == run_id)
                    .values(model_format=format)
                )
        except Exception:
            self._files.delete(path)
            raise


    def load_model(self, run_id: str) -> object:
        # Retrieve model format
        with self._db.engine.connect() as conn:
            format = conn.execute(
                select(runs.c.model_format)
                .where(runs.c.id == run_id)
            ).scalar_one_or_none()

        if format is None:
            raise ValueError(f"No saved model found for run: {run_id}")

        # Load and deserialize model
        serializer = get_serializer(format)
        data = self._files.load(f"{run_id}.{format}")

        return serializer.deserialize(data)