from contextlib import contextmanager
from typing import Generator
from datetime import datetime, UTC
from uuid import uuid4

import pandas as pd

from sqlalchemy import insert, delete, select, update

from .db import Database
from .db.schema import experiments, runs
from .query import Query


class MLLogs:
    # ======================
    # ----- Initialize -----
    # ======================

    def __init__(
        self,
        db_url: str = "sqlite:///.mllogs/mllogs.db",
    ) -> None:
        self._db = Database(db_url)
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
    def run(self, experiment_name: str) -> Generator[None]:
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
            yield
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

    def runs(self, experiment_name: str | None = None) -> Query:
        stmt = select(runs)

        if experiment_name is not None:
            stmt = (
                stmt.join(
                    experiments,
                    runs.c.experiment_id == experiments.c.id,
                )
                .where(experiments.c.name == experiment_name)
            )

        return Query(self._db, stmt)