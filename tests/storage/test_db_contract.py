from datetime import datetime, UTC
import pytest

from mllogs.artifact import ArtifactRef
from mllogs.run import Run, RunStatus
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
    return ArtifactRef(
        run_id="run-123",
        name="model",
        format="joblib",
    )


# ========================
# --- DBStore Contract ---
# ========================


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
    assert store.load_artifact_refs(run.id) == [artifact_ref]


def test_load_artifact_refs_empty(store, run):
    store.save_run(run)
    assert store.load_artifact_refs(run.id) == []


def test_load_artifact_refs_missing_run_raises_error(store):
    with pytest.raises(KeyError):
        store.load_artifact_refs("missing")