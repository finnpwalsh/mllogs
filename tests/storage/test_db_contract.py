from datetime import datetime, UTC
import pytest

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
        name="baseline",
        run_type="training",
        params={"learning_rate": 0.01, "epochs": 10},
        metrics={"accuracy": 0.95},
        tags={"model": "baseline"},
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


# ========================
# --- DBStore Contract ---
# ========================


# ===== SAVE =====

def test_save_and_load_run(store, run):
    store.save_run(run)
    assert store.load_run(run.id) == run


# ===== LOAD =====

def test_load_without_id_returns_latest(store, runs):
    for run in runs:
        store.save_run(run)
    assert store.load_run() == runs[2]


def test_load_missing_run_returns_none(store):
    assert store.load_run("missing") is None


# ===== LIST =====


def test_list_runs_without_limit(store, runs):
    for run in runs:
        store.save_run(run)

    result = store.list_runs()

    assert result == list(reversed(runs))


def test_list_runs_limit(store, runs):
    for run in runs:
        store.save_run(run)

    result = store.list_runs(limit=2)

    assert result == [runs[2], runs[1]]


def test_list_runs_invalid_limit(store):
    with pytest.raises(ValueError):
        store.list_runs(limit=0)


# ===== DELETE =====

def test_delete_run(store, run):
    store.save_run(run)
    store.delete_run(run.id)

    assert store.load_run(run.id) is None


def test_delete_missing_run(store):
    with pytest.raises(KeyError):
        store.delete_run("missing")