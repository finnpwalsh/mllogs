from datetime import datetime, UTC
import pytest

from mllogs.experiment import Experiment
from mllogs.artifact import ArtifactRef
from mllogs.run import Run, RunStatus
from mllogs.storage.db import SQLiteStore


# ================
# --- Fixtures ---
# ================


@pytest.fixture
def store(tmp_path):
    return SQLiteStore(tmp_path / "mllogs.db")

@pytest.fixture
def experiment(store):
    experiment = Experiment.create("ridge-finder")
    store.save_experiment(experiment)
    return experiment


@pytest.fixture
def run(experiment):
    return Run(
        id="run-123",
        started_at=datetime.now(UTC),
        status=RunStatus.COMPLETE,
        ended_at=datetime.now(UTC),
        experiment_id=experiment.id,
    )


@pytest.fixture
def artifact_ref():
    return ArtifactRef.create(
        run_id="run-123",
        name="model",
        format="joblib",
    )


# ===========================
# ----- SQLITE CONTRACT -----
# ===========================

def test_delete_experiment_sets_run_experiment_id_to_none(store, experiment, run):
    store.save_run(run)

    store.delete_experiment(experiment.id)

    retrieved_run = store.load_run(run.id)
    assert retrieved_run.experiment_id is None

def test_delete_run_cascades_child_rows(store, run, artifact_ref):
    store.save_run(run)
    
    store.save_param(run.id, "alpha", 0.1)
    store.save_metric(run.id, "accuracy", 0.95)
    store.save_tag(run.id, "model", "linear")
    store.save_artifact_ref(artifact_ref)

    store.delete_run(run.id)

    for table in ("params", "metrics", "tags", "artifacts"):
        row = store._connection.execute(
            f"""
            SELECT COUNT(*) AS count
            FROM {table}
            WHERE run_id = ?
            """,
            (run.id,),
        ).fetchone()

        assert row["count"] == 0