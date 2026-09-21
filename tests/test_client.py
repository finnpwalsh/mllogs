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


def test_start_run(client):
    client.start_run(
        name="run1",
        run_type="training",
    )

    with pytest.raises(RuntimeError):
        client.start_run()

    run = client._active_run

    # assert active run is generated
    assert run is not None

    # assert necessary fields are generated / populated
    assert run.started_at is not None
    assert run.id is not None
    assert run.status == RunStatus.RUNNING

    # assert passed parameters populate designated fields
    assert run.name == "run1"
    assert run.run_type == "training"

    # assert no additional fields are populated
    assert run.ended_at is None


def test_end_run(client):
    client.start_run()
    run = client.end_run()

    # assert active run is cleared
    assert client._active_run is None

    # assert ended run is complete
    assert run.status == RunStatus.COMPLETE
    assert run.ended_at is not None

    # assert ended run is persisted to storage
    assert client.get_run(run.id) == run


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