from typing import Any
from datetime import datetime, UTC
from uuid import uuid4

from .run import Run, RunStatus
from .storage import Storage

from .storage.db import SQLiteStore
from .storage.artifacts import LocalArtifactStore


class MLLogsClient:
    def __init__(self, storage: Storage | None = None):
        self._active_run: Run | None = None

        if storage is None:
            db = SQLiteStore()
            artifact_store = LocalArtifactStore()
            self._storage = Storage(db=db, artifact_store=artifact_store)
        else:
            self._storage = storage


    def _require_active_run(self) -> Run:
        if self._active_run is None:
            raise RuntimeError("No active run.")

        return self._active_run


    # ---------------------
    # --- Run Lifecycle ---
    # ---------------------
    
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
        if self._active_run is not None:
            raise RuntimeError("Active run already exists.")
        
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


    def end_run(self) -> Run:
        """
        End the active run. Clears the active run and persists to storage.

        Returns:
            - Active run
        """
        run = self._require_active_run()

        run.ended_at = datetime.now(UTC)
        run.status = RunStatus.COMPLETE

        self._storage.save_run(run)

        # clear run
        self._active_run = None

        return run


    # ---------------
    # --- Logging ---
    # ---------------
    
    def log_param(self, key: str, value: Any) -> None:
        run = self._require_active_run()
        run.params[key] = value


    def log_metric(self, key: str, value: float) -> None:
        run = self._require_active_run()
        run.metrics[key] = value


    def set_tag(self, key: str, value: str) -> None:
        run = self._require_active_run()
        run.tags[key] = value


    # -----------------------
    # --- Run persistence ---
    # -----------------------

    def get_run(self, run_id: str | None = None) -> Run | None:
        return self._storage.load_run(run_id=run_id)


    def list_runs(self, limit: int | None = None) -> list[Run]:
        return self._storage.list_runs(limit=limit)


    def delete_run(self, run_id: str) -> None:
        self._storage.delete_run(run_id=run_id)