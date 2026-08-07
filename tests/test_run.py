from datetime import datetime, UTC

from mllogs.run import Run, RunStatus, RunType


def test_create_run():
    run = Run(
        id="run-123",
        name="baseline",
        run_type=RunType.TRAIN,
        status=RunStatus.RUNNING,
        started_at=datetime.now(UTC),
    )

    assert run.id == "run-123"
    assert run.name == "baseline"
    assert run.run_type == RunType.TRAIN
    assert run.status == RunStatus.RUNNING