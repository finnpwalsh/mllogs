import pytest

from mllogs.run import RunStatus
from mllogs.client import MLLogsClient
from mllogs.storage import Storage
from mllogs.storage.db import SQLiteStore

# ====================
# ----- Fixtures -----
# ====================


@pytest.fixture
def client(tmp_path):
    storage=Storage(
        db=SQLiteStore(tmp_path / "mllogs.db")
    )
    return MLLogsClient(storage=storage)


# =================
# --- Start run ---
# =================

def test_start_run(client):
    client.start_run()

    run = client._active_run

    assert run is not None
    assert run.status == RunStatus.RUNNING
    assert run.ended_at is None

    assert client.get_run(run.id) == run


def test_start_run_with_active_run(client):
    client.start_run()

    with pytest.raises(RuntimeError):
        client.start_run()


# ==================
# --- Finish run ---
# ==================


def test_complete_run(client):
    client.start_run()
    run = client.complete_run()

    assert client._active_run is None
    assert run.status == RunStatus.COMPLETE
    assert run.ended_at is not None

    assert client.get_run(run.id) == run


def test_fail_run(client):
    client.start_run()
    run = client.fail_run()

    assert client._active_run is None
    assert run.status == RunStatus.FAILED
    assert run.ended_at is not None

    assert client.get_run(run.id) == run


# ================
# --- Log data ---
# ================


def test_log_run_data(client):
    client.start_run()

    # log param
    client.log_param("alpha", 0.1)
    assert client._active_run.params["alpha"] == 0.1

    # log metric
    client.log_metric("RMSE", 0.01)
    assert client._active_run.metrics["RMSE"] == 0.01

    # set tag
    client.set_tag("ml_model", "ridge")
    assert client._active_run.tags["ml_model"] == "ridge"


def test_ops_requiring_active_run(client):
    with pytest.raises(RuntimeError):
        client.log_param("alpha", 0.1)

    with pytest.raises(RuntimeError):
        client.log_metric("RMSE", 0.01)

    with pytest.raises(RuntimeError):
        client.set_tag("model", "ridge")

    with pytest.raises(RuntimeError):
        client.end_run()