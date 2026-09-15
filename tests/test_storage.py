from pathlib import Path
from datetime import datetime, UTC
import pytest

from mllogs.run import Run, RunStatus
from mllogs.storage import LocalFileStore


def test_persistence_round_trip(tmp_path: Path) -> None:
    storage = LocalFileStore(root_dir=tmp_path)

    run = Run(
        id="run123",
        status=RunStatus.RUNNING,
        started_at=datetime.now(UTC),
    )
    run_path = storage._runs_dir / f"{run.id}.json"

    # save
    storage.save_run(run)
    assert run_path.is_file()

    # load
    run_after = storage.load_run(run.id)
    assert run == run_after

    # delete
    storage.delete_run(run.id)
    assert not run_path.exists()


def test_list_runs(tmp_path: Path) -> None:
    storage = LocalFileStore(root_dir=tmp_path)

    for run_id in ["001", "002", "003"]:
        storage.save_run(Run(
            id=run_id,
            status=RunStatus.RUNNING,
            started_at=datetime.now(UTC),
        ))

    runs = storage.list_runs()

    assert [run.id for run in runs] == ["003", "002", "001"]


def test_list_runs_with_limit(tmp_path: Path) -> None:
    storage = LocalFileStore(root_dir=tmp_path)
    
    for run_id in ["001", "002", "003"]:
        storage.save_run(Run(
            id=run_id,
            status=RunStatus.RUNNING,
            started_at=datetime.now(UTC),
        ))

    runs = storage.list_runs(limit=2)

    assert [run.id for run in runs] == ["003", "002"]


def test_runs_with_invalid_limit(tmp_path: Path) -> None:
    storage = LocalFileStore(root_dir=tmp_path)

    with pytest.raises(ValueError):
        storage.list_runs(limit=0)


def test_load_latest_run(tmp_path: Path) -> None:
    storage = LocalFileStore(root_dir=tmp_path)
        
    run1 = Run(
        id="001",
        status=RunStatus.RUNNING,
        started_at=datetime.now(UTC),
    )

    run2 = Run(
        id="002",
        status=RunStatus.RUNNING,
        started_at=datetime.now(UTC),
    )

    storage.save_run(run1)
    storage.save_run(run2)

    latest_run = storage.load_run()

    assert latest_run == run2