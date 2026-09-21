import pytest

from mllogs.query import Query
from mllogs.run import Run
from mllogs.storage.db import SQLiteStore


@pytest.fixture
def store(tmp_path):
    return SQLiteStore(tmp_path / "mllogs.db")


@pytest.fixture
def query(store):
    return Query(store)


@pytest.fixture
def run(store):
    run = Run.create()
    store.save_run(run)
    return run


def test_get_run(query, run):
    loaded = query.get_run(run.id)

    assert loaded == run


def test_get_run_not_found(query):
    with pytest.raises(KeyError):
        query.get_run("missing")


def test_get_params(query, store, run):
    params = {
        "alpha": 0.1,
        "count": 3,
        "enabled": True,
        "method": "linear",
    }

    for key, value in params.items():
        store.save_param(
            run_id=run.id,
            key=key,
            value=value,
        )

    assert query.get_params(run.id) == params


def test_get_metrics(query, store, run):
    metrics = {
        "RMSE": 0.01,
        "MAE": 0.05,
    }

    for key, value in metrics.items():
        store.save_metric(
            run_id=run.id,
            key=key,
            value=value,
        )

    assert query.get_metrics(run.id) == metrics


def test_get_tags(query, store, run):
    tags = {
        "model": "ridge",
        "dataset": "train",
    }

    for key, value in tags.items():
        store.save_tag(
            run_id=run.id,
            key=key,
            value=value,
        )

    assert query.get_tags(run.id) == tags