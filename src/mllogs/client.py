from typing import Any
from datetime import datetime, UTC
from uuid import uuid4

from .run import Run, RunStatus
from .storage import LocalFileStore


class MLLogsClient:
    def __init__(self, file_store: LocalFileStore | None = None):
        self._active_run: Run | None = None
        self._file_store = file_store if file_store is not None else LocalFileStore()

    def start_run(
            self,
            name: str | None = None,
            run_type: str | None = None,
    ) -> None:
        """
        Start a new MLLogs run.

        Args:
            name: Optional name for the run.
            run_type: Optional type used to categorize the run.
        """
        # generate run id
        started_at = datetime.now(UTC)
        timestamp = started_at.strftime("%Y%m%d%H%M%S")
        random_suffix = uuid4().hex[:8]
        run_id = f"{timestamp}-{random_suffix}"

        self._active_run = Run(
            id=run_id,
            name=name,
            run_type=run_type,
            status = RunStatus.RUNNING,
            started_at=started_at,
        )
        # END


    def log_param(self, key: str, value: Any) -> None:
        self._active_run.params[key] = value


    def log_metric(self, key: str, value: float) -> None:
        self._active_run.metrics[key] = value


    def set_tag(self, key: str, value: str) -> None:
        self._active_run.tags[key] = value


    def end_run(self) -> Run:
        if self._active_run is None:
            raise RuntimeError("No active run.")

        run = self._active_run

        run.ended_at = datetime.now(UTC)
        run.status = RunStatus.COMPLETE

        self._file_store.save_run(run)

        # clear run
        self._active_run = None

        return run