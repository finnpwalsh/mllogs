import pytest

from mllogs import MLLogs
from mllogs.run import RunStatus


# =================
# --- Fixtures ---
# =================

@pytest.fixture
def mll(tmp_path):
    return MLLogs(tmp_path)


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
    assert mll.query.list_experiments() == [experiment]


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

@pytest.fixture
def artifact_ref(mll):
    mll.start_run()

    obj = {"alpha": 0.01}

    return mll.save_artifact(
        name="model",
        obj=obj,
        format="joblib"
    )

def test_artifact_round_trip(mll, artifact_ref):
    assert mll.query.load_artifact(artifact_ref.run_id, artifact_ref.name) == {"alpha": 0.01}


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


# ======================
# ----- Load Model -----
# ======================

@pytest.fixture
def model_versions(mll):
    mll.create_experiment("test-experiment")
    mll.start_run("test-experiment")

    versions = []

    for alpha in [0.1, 1.0, 10]:
        model = {"alpha": alpha}

        artifact_ref = mll.save_artifact(f"model-{alpha}", model, "joblib")
        
        version = mll.registry.create_version("test-model", artifact_ref)
        versions.append(version)

    mll.complete_run()
    return versions

def test_load_model_latest(mll, model_versions):
    assert mll.registry.load_model("test-model") == {"alpha": 10.0}

def test_load_model_by_version(mll, model_versions):
    assert mll.registry.load_model("test-model", version=2) == {"alpha": 1.0}

def test_load_model_by_alias(mll, model_versions):
    mll.registry.set_alias(model_versions[1], "champion")

    assert mll.registry.load_model("test-model", alias="champion") == {"alpha": 1.0}


def test_load_model_version_and_alias(mll):
    with pytest.raises(ValueError):
        mll.registry.load_model(
            "test-model",
            version=1,
            alias="champion",
        )