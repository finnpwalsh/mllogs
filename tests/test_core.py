import pytest

from mllogs import MLLogs
from mllogs.storage.db import SQLiteStore


# =================
# --- Fixtures ---
# =================

@pytest.fixture
def mll(tmp_path):
    db_store = SQLiteStore(tmp_path / "mllogs.db")
    return MLLogs(db_store)


# =================
# --- Start run ---
# =================

def test_start_run_persists_run(mll):
    mll.tracker.start_run()

    run = mll.tracker.active_run

    assert mll.query.get_run(run.id) == run


# ==================
# --- Finish run ---
# ==================


def test_complete_run_round_trip(mll):
    mll.tracker.start_run()
    run = mll.tracker.complete_run()

    assert mll.query.get_run(run.id) == run


def test_fail_run_round_trip(mll):
    mll.tracker.start_run()
    run = mll.tracker.fail_run()

    assert mll.query.get_run(run.id) == run


# ================
# --- Log data ---
# ================


def test_param_round_trip(mll):
    mll.tracker.start_run()
    run_id = mll.tracker.active_run.id

    params = {
        "alpha": 0.1,
        "count": 3,
        "enabled": True,
        "method": "linear",
    }

    for key, value in params.items():
        mll.tracker.log_param(key, value)

    assert mll.query.get_params(run_id) == params


def test_metric_round_trip(mll):
    mll.tracker.start_run()
    run_id = mll.tracker.active_run.id

    mll.tracker.log_metric("RMSE", 0.01)

    assert mll.query.get_metrics(run_id) == {"RMSE": 0.01}


def test_tag_round_trip(mll):
    mll.tracker.start_run()
    run_id = mll.tracker.active_run.id

    mll.tracker.set_tag("model", "ridge")

    assert mll.query.get_tags(run_id) == {"model": "ridge"}