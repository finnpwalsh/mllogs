from typing import Any
from datetime import datetime, UTC

from .run import Run, RunStatus
from .storage import Storage

from .storage.db import SQLiteStore


class MLLogsClient:
    def __init__(self, storage: Storage | None = None):
        self._active_run: Run | None = None

        if storage is None:
            db = SQLiteStore()
            self._storage = Storage(db=db)
        else:
            self._storage = storage


    def _require_active_run(self) -> Run:
        if self._active_run is None:
            raise RuntimeError("No active run.")

        return self._active_run


    # =============
    # --- TRACK ---
    # =============
    
    def start_run(self) -> None:
        """
        Start and persist a new run.
        """
        if self._active_run is not None:
            raise RuntimeError("Active run already exists.")
        
        run = Run.create()

        self._storage.save_run(run)
        self._active_run = run


    def complete_run(self) -> Run:
        """
        Complete and persist the active run.
        """
        run = self._require_active_run()

        run.ended_at = datetime.now(UTC)
        run.status = RunStatus.COMPLETE

        self._storage.update_run(run)
        self._active_run = None

        return run


    def fail_run(self) -> Run:
        """
        Fail and persist the active run.
        """
        run = self._require_active_run()

        run.ended_at = datetime.now(UTC)
        run.status = RunStatus.FAILED

        self._storage.update_run(run)
        self._active_run = None

        return run
    
    
    def log_param(self, key: str, value: Any) -> None:
        run = self._require_active_run()
        run.params[key] = value


    def log_metric(self, key: str, value: float) -> None:
        run = self._require_active_run()
        run.metrics[key] = value


    def set_tag(self, key: str, value: str) -> None:
        run = self._require_active_run()
        run.tags[key] = value


    # =============
    # --- Query ---
    # =============

    def get_run(self, run_id: str | None = None) -> Run | None:
        return self._storage.load_run(run_id=run_id)


    def list_runs(self, limit: int | None = None) -> list[Run]:
        return self._storage.list_runs(limit=limit)