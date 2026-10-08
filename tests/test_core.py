import pytest

from mllogs import MLLogs
from mllogs.run import RunStatus
from mllogs.storage.db import SQLiteStore
from mllogs.storage.artifacts import LocalArtifactStore


# =================
# --- Fixtures ---
# =================

@pytest.fixture
def mll(tmp_path):
    db_store = SQLiteStore(tmp_path / "mllogs.db")
    artifact_store = LocalArtifactStore(tmp_path / ".mllogs")
    return MLLogs(db_store, artifact_store)


# ================
# ----- Runs -----
# ================

def test_start_run(mll):
    mll.start_run()

    run = mll._active_run

    assert run is not None
    assert run.status == RunStatus.RUNNING
    assert run.ended_at is None


def test_start_run_with_active_run(mll):
    mll.start_run()

    with pytest.raises(RuntimeError):
        mll.start_run()


def test_complete_run(mll):
    mll.start_run()
    run = mll.complete_run()

    assert mll._active_run is None
    assert run.status == RunStatus.COMPLETE
    assert run.ended_at is not None


def test_fail_run(mll):
    mll.start_run()
    run = mll.fail_run()

    assert mll._active_run is None
    assert run.status == RunStatus.FAILED
    assert run.ended_at is not None


def test_start_run_persists_run(mll):
    mll.start_run()

    run = mll._active_run

    assert mll.query.get_run(run.id) == run


# ===================
# --- Round Trips ---
# ===================

# ===== EXPERIMENTS =====

def test_experiment_round_trip(mll):
    experiment = mll.create_experiment("ridge-test")
    assert mll.query.get_experiment_by_name(experiment.name) == experiment


# ===== RUNS =====

def test_complete_run_round_trip(mll):
    mll.start_run()
    run = mll.complete_run()

    assert mll.query.get_run(run.id) == run


def test_fail_run_round_trip(mll):
    mll.start_run()
    run = mll.fail_run()

    assert mll.query.get_run(run.id) == run


def test_multiple_runs_round_trip(mll):
    experiment = mll.create_experiment("ridge-test")

    runs = []

    for _ in range(3):
        mll.start_run(experiment.name)
        runs.append(mll.complete_run())

    assert mll.query.list_runs(experiment.name) == list(reversed(runs))


# ===== DATA =====

def test_param_round_trip(mll):
    mll.start_run()
    run_id = mll._active_run.id

    params = {
        "alpha": 0.1,
        "count": 3,
        "enabled": True,
        "method": "linear",
    }

    for key, value in params.items():
        mll.log_param(key, value)

    assert mll.query.get_params(run_id) == params


def test_metric_round_trip(mll):
    mll.start_run()
    run_id = mll._active_run.id

    mll.log_metric("RMSE", 0.01)

    assert mll.query.get_metrics(run_id) == {"RMSE": 0.01}


def test_tag_round_trip(mll):
    mll.start_run()
    run_id = mll._active_run.id

    mll.set_tag("model", "ridge")

    assert mll.query.get_tags(run_id) == {"model": "ridge"}


# ===== ARTIFACTS =====

def test_artifact_round_trip(mll):
    mll.start_run()
    run_id = mll._active_run.id

    obj = {"alpha": 0.01}

    mll.save_artifact(
        name="model",
        obj=obj,
        format="joblib",
    )

    assert mll.query.load_artifact(run_id, "model") == obj


# ==========================
# ----- Data Contracts -----
# ==========================

def test_start_run_with_experiment_id_without_experiment_raises(mll):
    with pytest.raises(KeyError):
        mll.start_run("ridge-test")

def test_ops_requiring_active_run(mll):
    with pytest.raises(RuntimeError):
        mll.log_param("alpha", 0.1)

    with pytest.raises(RuntimeError):
        mll.log_metric("RMSE", 0.01)

    with pytest.raises(RuntimeError):
        mll.set_tag("model", "ridge")

    with pytest.raises(RuntimeError):
        mll.complete_run()

    with pytest.raises(RuntimeError):
        mll.fail_run()