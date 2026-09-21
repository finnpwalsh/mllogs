import pytest

from mllogs.run import RunStatus
from mllogs.types import ParamValue
from mllogs import MLLogs
from mllogs.storage.db import SQLiteStore

# ====================
# ----- Fixtures -----
# ====================


@pytest.fixture
def ml(tmp_path):
    db_store = SQLiteStore(tmp_path / "mllogs.db")
    return MLLogs(db_store)


# =================
# --- Start run ---
# =================

def test_start_run(ml):
    ml.start_run()

    run = ml.active_run

    assert run is not None
    assert run.status == RunStatus.RUNNING
    assert run.ended_at is None

    assert ml.query.get_run(run.id) == run


def test_start_run_with_active_run(ml):
    ml.start_run()

    with pytest.raises(RuntimeError):
        ml.start_run()


# ==================
# --- Finish run ---
# ==================


def test_complete_run(ml):
    ml.start_run()
    run = ml.complete_run()

    assert ml.active_run is None
    assert run.status == RunStatus.COMPLETE
    assert run.ended_at is not None

    assert ml.query.get_run(run.id) == run


def test_fail_run(ml):
    ml.start_run()
    run = ml.fail_run()

    assert ml._active_run is None
    assert run.status == RunStatus.FAILED
    assert run.ended_at is not None

    assert ml.query.get_run(run.id) == run


# ================
# --- Log data ---
# ================


def test_log_param(ml):
    ml.start_run()

    run_id = ml.active_run.id

    params: dict[str, ParamValue] = {
        "alpha": 0.1,
        "count": 3,
        "enabled": True,
        "method": "linear",
    }

    for key, value in params.items():
        ml.log_param(key, value)

    assert ml.query.get_params(run_id) == params


def test_log_metric(ml):
    ml.start_run()

    run_id = ml.active_run.id

    ml.log_metric("RMSE", 0.01)

    assert ml.query.get_metrics(run_id) == {"RMSE": 0.01}


def test_set_tag(ml):
    ml.start_run()

    run_id = ml.active_run.id

    ml.set_tag("model", "ridge")

    assert ml.query.get_tags(run_id) == {"model": "ridge"}



def test_ops_requiring_active_run(ml):
    with pytest.raises(RuntimeError):
        ml.log_param("alpha", 0.1)

    with pytest.raises(RuntimeError):
        ml.log_metric("RMSE", 0.01)

    with pytest.raises(RuntimeError):
        ml.set_tag("model", "ridge")

    with pytest.raises(RuntimeError):
        ml.complete_run()

    with pytest.raises(RuntimeError):
        ml.fail_run()