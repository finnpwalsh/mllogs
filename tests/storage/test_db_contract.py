from datetime import datetime, UTC
import pytest

from mllogs.artifact import ArtifactRef
from mllogs.experiment import Experiment
from mllogs.run import Run, RunStatus
from mllogs.storage.db import SQLiteStore
from mllogs.model.models import RegisteredModel, ModelVersion


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

@pytest.fixture
def experiment(store):
    experiment = Experiment.create("ridge-finder")
    store.save_experiment(experiment)
    return experiment


@pytest.fixture
def run():
    return Run(
        id="run-123",
        started_at=datetime.now(UTC),
        status=RunStatus.COMPLETE,
        ended_at=datetime.now(UTC),
    )


@pytest.fixture
def runs():
    return [
        Run(
            id="run-1",
            started_at=datetime(2000, 1, 1, tzinfo=UTC),
            status=RunStatus.COMPLETE,
        ),
        Run(
            id="run-2",
            started_at=datetime(2000, 1, 2, tzinfo=UTC),
            status=RunStatus.COMPLETE,
        ),
        Run(
            id="run-3",
            started_at=datetime(2000, 1, 3, tzinfo=UTC),
            status=RunStatus.COMPLETE,
        ),
    ]


@pytest.fixture
def artifact_ref():
    return ArtifactRef.create(
        run_id="run-123",
        name="model",
        format="joblib",
    )


# ========================
# --- DBStore Contract ---
# ========================

# ===== EXPERIMENTS =====

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


# ===== RUNS =====

def test_save_and_load_run(store, run):
    store.save_run(run)
    assert store.load_run(run.id) == run


def test_load_missing_run_raises_error(store):
    with pytest.raises(KeyError):
        store.load_run("missing")


def test_delete_run(store, run):
    store.save_run(run)
    store.delete_run(run.id)

    with pytest.raises(KeyError):
        store.load_run(run.id)


def test_delete_missing_run_raises_error(store):
    with pytest.raises(KeyError):
        store.delete_run("missing")


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
    store.save_run(run)
    store.save_param(run.id, key, value)
    params = store.load_params(run.id)
    assert params[key] == value


def test_load_params_empty(store, run):
    store.save_run(run)
    assert store.load_params(run.id) == {}


def test_load_params_missing_run_raises_error(store):
    with pytest.raises(KeyError):
        store.load_params("missing")


# ===== METRICS =====

def test_metric_round_trip(store, run):
    store.save_run(run)
    store.save_metric(run.id, "accuracy", 0.95)

    assert store.load_metrics(run.id) == {"accuracy": 0.95}


def test_load_metrics_empty(store, run):
    store.save_run(run)
    assert store.load_metrics(run.id) == {}


def test_load_metrics_missing_run_raises_error(store):
    with pytest.raises(KeyError):
        store.load_metrics("missing")


# ===== TAGS =====

def test_tag_round_trip(store, run):
    store.save_run(run)
    store.save_tag(run.id, "model", "linear")

    assert store.load_tags(run.id) == {"model": "linear"}


def test_load_tags_empty(store, run):
    store.save_run(run)
    assert store.load_tags(run.id) == {}


def test_load_tags_missing_run_raises_error(store):
    with pytest.raises(KeyError):
        store.load_tags("missing")


# ===== ARTIFACT REFS =====

def test_artifact_ref_round_trip(store, run, artifact_ref):
    store.save_run(run)
    store.save_artifact_ref(artifact_ref)
    
    assert store.load_artifact_ref(artifact_ref.id) == artifact_ref
    assert store.load_artifact_ref_by_name(artifact_ref.run_id, artifact_ref.name) == artifact_ref

def test_load_artifact_refs_empty(store, run):
    store.save_run(run)
    assert store.load_artifact_refs(run.id) == []

def test_load_artifact_refs_missing_run_raises_error(store):
    with pytest.raises(KeyError):
        store.load_artifact_refs("missing")


# ===== MODELS =====

@pytest.fixture
def registered_model():
    return RegisteredModel.create(name="linear_regression")

@pytest.fixture
def model_version(registered_model, artifact_ref):
    return ModelVersion.create(
        model_id=registered_model.id,
        version=1,
        artifact_id=artifact_ref.id,
    )

@pytest.fixture
def model_versions(registered_model, artifact_ref):
    return [
        ModelVersion.create(
            model_id=registered_model.id,
            version=version,
            artifact_id=artifact_ref.id,
        )
        for version in [1, 2, 3]
    ]

def test_registered_model_round_trip(store, registered_model):
    store.save_registered_model(registered_model)
    assert store.load_registered_model(registered_model.id) == registered_model
    assert store.load_registered_model_by_name(registered_model.name) == registered_model

def test_model_version_round_trip(
    store, 
    run,
    artifact_ref,
    registered_model,
    model_version,

):
    store.save_run(run)
    store.save_artifact_ref(artifact_ref)
    store.save_registered_model(registered_model)
    store.save_model_version(model_version)

    assert store.load_model_version(model_version.id) == model_version
    assert store.load_model_version_by_model(model_version.model_id, model_version.version) == model_version

def test_load_model_versions(
    store,
    run,
    artifact_ref,
    registered_model,
    model_versions,
):
    store.save_run(run)
    store.save_artifact_ref(artifact_ref)
    store.save_registered_model(registered_model)

    for model_version in model_versions:
        store.save_model_version(model_version)

    assert store.load_model_versions(registered_model.id) == model_versions
    assert store.load_latest_model_version(registered_model.id).version == 3