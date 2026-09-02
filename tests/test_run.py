from datetime import datetime, UTC

from mllogs.run import Run, RunStatus


def test_run_defaults():
    started_at = datetime(2000, 1, 1, 0, 0, tzinfo=UTC)
    run = Run(
        id="run-123",
        status=RunStatus.RUNNING,
        started_at=started_at,
    )

    assert run.name is None
    assert run.run_type is None
    assert run.ended_at is None
    assert run.params == {}
    assert run.metrics == {}
    assert run.tags == {}
    assert run.artifacts == []


def test_to_dict():
    started_at = datetime(2000, 1, 1, 0, 0, tzinfo=UTC)
    run = Run(
        id="run-123",
        status=RunStatus.RUNNING,
        started_at=started_at,
    )

    d = run.to_dict()

    assert d["id"] == "run-123"
    assert d["status"] == "running"
    assert d["started_at"] == "2000-01-01T00:00:00+00:00"


def test_from_dict():
    d = {
        "id": "run-123",
        "status": "running",
        "started_at": "2000-01-01T00:00:00+00:00",
        "name": None,
        "run_type": None,
        "ended_at": None,
        "params": {},
        "metrics": {},
        "tags": {},
        "artifacts": [],
    }

    run = Run.from_dict(d)

    assert run.started_at == datetime(2000, 1, 1, 0, 0, tzinfo=UTC)
    assert run.status == RunStatus.RUNNING


def test_round_trip():
    started_at = datetime(2000, 1, 1, 0, 0, tzinfo=UTC)

    before = Run(
        id="run-123",
        status=RunStatus.RUNNING,
        started_at=started_at,
    )

    after = Run.from_dict(before.to_dict())

    assert before == after