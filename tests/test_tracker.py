import pytest

from mllogs.run import RunStatus
from mllogs.tracker import Tracker
from mllogs.storage.db import SQLiteStore

# ====================
# ----- Fixtures -----
# ====================


@pytest.fixture
def tracker(tmp_path):
    db_store = SQLiteStore(tmp_path / "mllogs.db")
    return Tracker(db_store)


# =================
# --- Start run ---
# =================

def test_start_run(tracker):
    tracker.start_run()

    run = tracker.active_run

    assert run is not None
    assert run.status == RunStatus.RUNNING
    assert run.ended_at is None


def test_start_run_with_active_run(tracker):
    tracker.start_run()

    with pytest.raises(RuntimeError):
        tracker.start_run()


def test_ops_requiring_active_run(tracker):
    with pytest.raises(RuntimeError):
        tracker.log_param("alpha", 0.1)

    with pytest.raises(RuntimeError):
        tracker.log_metric("RMSE", 0.01)

    with pytest.raises(RuntimeError):
        tracker.set_tag("model", "ridge")

    with pytest.raises(RuntimeError):
        tracker.complete_run()

    with pytest.raises(RuntimeError):
        tracker.fail_run()


# ==================
# --- Finish run ---
# ==================


def test_complete_run(tracker):
    tracker.start_run()
    run = tracker.complete_run()

    assert tracker.active_run is None
    assert run.status == RunStatus.COMPLETE
    assert run.ended_at is not None


def test_fail_run(tracker):
    tracker.start_run()
    run = tracker.fail_run()

    assert tracker.active_run is None
    assert run.status == RunStatus.FAILED
    assert run.ended_at is not None