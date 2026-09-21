from mllogs.run import Run, RunStatus


def test_create_run():
    run = Run.create()

    timestamp, uuid = run.id.split("-")

    assert timestamp == run.started_at.strftime("%Y%m%d%H%M%S")
    assert len(uuid) == 8
    assert run.status == RunStatus.RUNNING
    assert run.ended_at is None