from datetime import datetime, UTC, timedelta

import pytest
from sqlalchemy import insert

from mllogs.new.client import MLLogs
from mllogs.new.db import Database
from mllogs.new.db.schema import experiments, runs


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
    client = MLLogs(f"sqlite:///{tmp_path / 'client.db'}")
    yield client
    client.close()


# =======================
# ----- Sample Data -----
# =======================

@pytest.fixture
def experiment(db):
    with db.engine.begin() as conn:
        conn.execute(
            insert(experiments).values(
                id="exp-001",
                name="test",
                created_at=datetime.now(UTC),
            )
        )

    return "exp-001"


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