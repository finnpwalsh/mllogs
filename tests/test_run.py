from datetime import datetime, UTC

from mllogs.run import Run, RunStatus


def test_create_run():
    run = Run(
        id="run-123",
        name="baseline",
        run_type="training",
        status=RunStatus.RUNNING,
        started_at=datetime.now(UTC),
    )

    assert run.id == "run-123"
    assert run.name == "baseline"
    assert run.run_type == "training"
    assert run.status == RunStatus.RUNNING


def test_to_dict():
    started_at = datetime(2000, 1, 1, 0, 0, tzinfo=UTC)
    run = Run(
        id="run-123",
        name="baseline",
        run_type="training",
        status=RunStatus.RUNNING,
        started_at=started_at,
    )

    assert run.to_dict() == {
        "id": "run-123",
        "name": "baseline",
        "run_type": "training",
        "status": "running",
        "started_at": "2000-01-01T00:00:00+00:00",
        "ended_at": None,
        "params": {},
        "metrics": {},
        "tags": {},
        "artifacts": None,
    }