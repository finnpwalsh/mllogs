from datetime import datetime, UTC, timedelta

import pytest
from sqlalchemy import insert, select

from mllogs.new.client import MLLogs
from mllogs.new.storage.db import Database
from mllogs.new.storage.db.schema import (
    experiments,
    runs,
    params,
    metrics,
    tags,
)
from mllogs.new.query import Query, RunsQuery


# ==========================
# ----- Infrastructure -----
# ==========================

@pytest.fixture
def db(tmp_path):
    database = Database(f"sqlite:///{tmp_path / 'test.db'}")
    yield database
    database.close()


@pytest.fixture
def mll(tmp_path):
    client = MLLogs(
        db_url=f"sqlite:///{tmp_path / 'client.db'}",
        file_url=str(tmp_path / "models")
    )
    yield client
    client.close()


# =====================
# ----- Queries -----
# =====================

@pytest.fixture
def query(db, sample_runs):
    return Query(db, select(runs))


@pytest.fixture
def runs_query(db, sample_run_data):
    return RunsQuery(db, select(runs))


# ==========================
# ----- Experiments -----
# ==========================

@pytest.fixture
def experiment(db):
    experiment_id = "exp-001"

    with db.engine.begin() as conn:
        conn.execute(
            insert(experiments).values(
                id=experiment_id,
                name="test",
                created_at=datetime.now(UTC),
            )
        )

    return experiment_id


# =====================
# ----- Runs -----
# =====================

@pytest.fixture
def sample_runs(db, experiment):
    now = datetime.now(UTC)

    with db.engine.begin() as conn:
        conn.execute(
            insert(runs),
            [
                {
                    "id": "run-001",
                    "experiment_id": experiment,
                    "started_at": now,
                    "status": "COMPLETE",
                },
                {
                    "id": "run-002",
                    "experiment_id": experiment,
                    "started_at": now + timedelta(minutes=1),
                    "status": "FAILED",
                },
                {
                    "id": "run-003",
                    "experiment_id": experiment,
                    "started_at": now + timedelta(minutes=2),
                    "status": "COMPLETE",
                },
            ],
        )

    return ["run-001", "run-002", "run-003"]


# =========================
# ----- Parameters -----
# =========================

@pytest.fixture
def sample_params(db, sample_runs):
    with db.engine.begin() as conn:
        conn.execute(
            insert(params),
            [
                {"run_id": "run-001", "key": "alpha", "value": 0.1},
                {"run_id": "run-002", "key": "alpha", "value": 1.0},
            ],
        )


# ======================
# ----- Metrics -----
# ======================

@pytest.fixture
def sample_metrics(db, sample_runs):
    with db.engine.begin() as conn:
        conn.execute(
            insert(metrics),
            [
                {"run_id": "run-001", "key": "mse", "value": 0.45},
                {"run_id": "run-002", "key": "mse", "value": 0.38},
                {"run_id": "run-003", "key": "mse", "value": 0.42},
            ],
        )


# ===================
# ----- Tags -----
# ===================

@pytest.fixture
def sample_tags(db, sample_runs):
    with db.engine.begin() as conn:
        conn.execute(
            insert(tags).values(
                run_id="run-001",
                key="dataset",
                value="diabetes",
            )
        )


# ==============================
# ----- Full Run Dataset -----
# ==============================

@pytest.fixture
def sample_run_data(sample_params, sample_metrics, sample_tags):
    pass