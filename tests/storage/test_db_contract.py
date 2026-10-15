import pytest

from mllogs.artifact import ArtifactRef
from mllogs.experiment import Experiment
from mllogs.run import Run
from mllogs.storage.db import SQLiteStore


# ================
# --- Fixtures ---
# ================

DB_STORES = [
    SQLiteStore,
    # e.g. DuckDBStore in future
]


@pytest.fixture(params=DB_STORES)
def store(request, tmp_path):
    store_class = request.param
    return store_class(tmp_path / "mllogs.db")


# ========================
# --- DBStore Contract ---
# ========================

# ===== EXPERIMENTS =====

@pytest.fixture
def experiment(store):
    experiment = Experiment.create("ridge-finder")
    store.save_experiment(experiment)
    return experiment

@pytest.fixture
def experiments(store):
    experiments = [
    Experiment.create(name)
    for name in ["ridge-test", "lasso-test", "tree-test"]
    ]
    for experiment in experiments:
        store.save_experiment(experiment)

    return experiments

def test_experiment_round_trip(store, experiment):
    assert store.load_experiment(experiment.id) == experiment
    assert store.load_experiment_by_name(experiment.name) == experiment

def test_delete_experiment(store, experiment):
    store.delete_experiment(experiment.id)

    with pytest.raises(KeyError):
        store.load_experiment(experiment.id)

def test_missing_experiment_raises_error(store):
    with pytest.raises(KeyError):
        store.load_experiment("experiment-123")

    with pytest.raises(KeyError):
        store.load_experiment_by_name("ridge-finder")

    with pytest.raises(KeyError):
        store.delete_experiment("experiment-123")

def test_load_experiments(store, experiments):
    assert store.load_experiments() == list(reversed(experiments))


# ===== RUNS =====

@pytest.fixture
def run(store):
    run = Run.create()

    store.save_run(run)
    return run
    
@pytest.fixture
def runs(store):
    runs = []
    for _ in range(3):
        run = Run.create()
        store.save_run(run)
        runs.append(run)
    
    return runs

@pytest.fixture
def runs_with_experiment_id(store, experiment):
    runs = []

    for _ in range(3):
        run = Run.create(experiment.id)
        store.save_run(run)
        runs.append(run)

    return runs

def test_run_round_trip(store, run):
    assert store.load_run(run.id) == run

def test_load_missing_run_raises_error(store):
    with pytest.raises(KeyError):
        store.load_run("missing")

def test_delete_run(store, run):
    store.delete_run(run.id)

    with pytest.raises(KeyError):
        store.load_run(run.id)

def test_delete_missing_run_raises_error(store):
    with pytest.raises(KeyError):
        store.delete_run("missing")

def test_save_and_load_runs(store, runs):
    assert store.load_runs() == list(reversed(runs))

def test_save_and_load_runs_with_experiment_id(store, experiment, runs_with_experiment_id):
    store.save_run(Run.create())
    assert store.load_runs(experiment.id) == list(reversed(runs_with_experiment_id))


# ===== PARAMS =====

@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("alpha", 0.1),
        ("count", 3),
        ("enabled", True),
        ("method", "linear"),
    ]
)

def test_param_round_trip(store, run, key, value):
    store.save_param(run.id, key, value)
    params = store.load_params(run.id)
    assert params[key] == value

def test_load_params_empty(store, run):
    assert store.load_params(run.id) == {}

def test_load_params_missing_run_raises_error(store):
    with pytest.raises(KeyError):
        store.load_params("missing")


# ===== METRICS =====

def test_metric_round_trip(store, run):
    store.save_metric(run.id, "accuracy", 0.95)
    assert store.load_metrics(run.id) == {"accuracy": 0.95}

def test_load_metrics_empty(store, run):
    assert store.load_metrics(run.id) == {}

def test_load_metrics_missing_run_raises_error(store):
    with pytest.raises(KeyError):
        store.load_metrics("missing")


# ===== TAGS =====

def test_tag_round_trip(store, run):
    store.save_tag(run.id, "model", "linear")
    assert store.load_tags(run.id) == {"model": "linear"}

def test_load_tags_empty(store, run):
    assert store.load_tags(run.id) == {}

def test_load_tags_missing_run_raises_error(store):
    with pytest.raises(KeyError):
        store.load_tags("missing")


# ===== ARTIFACT REFS =====

@pytest.fixture
def artifact_ref(store, run):
    ref = ArtifactRef.create(
        run_id=run.id,
        name="model",
        format="joblib",
    )

    store.save_artifact_ref(ref)
    return ref

def test_artifact_ref_round_trip(store, artifact_ref):
    assert store.load_artifact_ref(artifact_ref.id) == artifact_ref
    assert store.load_artifact_ref_by_name(artifact_ref.run_id, artifact_ref.name) == artifact_ref

def test_load_artifact_refs_empty(store, run):
    assert store.load_artifact_refs(run.id) == []

def test_load_artifact_refs_missing_run_raises_error(store):
    with pytest.raises(KeyError):
        store.load_artifact_refs("missing")