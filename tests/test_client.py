from mllogs.run import RunStatus
from mllogs.client import MLLogsClient


def test_start_run() -> None:
    client = MLLogsClient()
    client.start_run(
        name="run1",
        run_type="training",
    )

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


def test_end_run() -> None:
    client = MLLogsClient()

    client.start_run()
    client.end_run()

    assert client._active_run is None


def test_mutate_params() -> None:
    client = MLLogsClient()

    client.start_run()

    # log param
    client.log_param("alpha", 0.1)
    assert "alpha" in client._active_run.params.keys()
    assert client._active_run.params["alpha"] == 0.1

    # log metric
    client.log_metric("RMSE", 0.01)
    assert "RMSE" in client._active_run.metrics.keys()
    assert client._active_run.metrics["RMSE"] == 0.01

    # set tag
    client.set_tag("ml_model", "ridge")
    assert "ml_model" in client._active_run.tags.keys()
    assert client._active_run.tags["ml_model"] == "ridge"
