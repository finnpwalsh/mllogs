from datetime import datetime, UTC

from .run import Run, RunStatus
from .types import ParamValue
from .query import Query

from .storage.db import DBStore, SQLiteStore


class MLLogs:
    def __init__(self, db_store: DBStore | None = None):
        self._active_run: Run | None = None
        self._db_store = db_store or SQLiteStore()

        self.query = Query(self._db_store)


    def _require_active_run(self) -> Run:
        if self._active_run is None:
            raise RuntimeError("No active run.")

        return self._active_run

    
    def start_run(self) -> None:
        """
        Start and persist a new run.
        """
        if self._active_run is not None:
            raise RuntimeError("Active run already exists.")
        
        run = Run.create()

        self._db_store.save_run(run)
        self._active_run = run


    def complete_run(self) -> Run:
        """
        Complete and persist the active run.
        """
        run = self._require_active_run()

        run.ended_at = datetime.now(UTC)
        run.status = RunStatus.COMPLETE

        self._db_store.update_run(run)
        self._active_run = None

        return run


    def fail_run(self) -> Run:
        """
        Fail and persist the active run.
        """
        run = self._require_active_run()

        run.ended_at = datetime.now(UTC)
        run.status = RunStatus.FAILED

        self._db_store.update_run(run)
        self._active_run = None

        return run


    def log_param(self, key: str, value: ParamValue) -> None:
        run = self._require_active_run()
        self._db_store.save_param(
            run_id=run.id,
            key=key,
            value=value,
        )


    def log_metric(self, key: str, value: float) -> None:
        run = self._require_active_run()
        self._db_store.save_metric(
            run_id=run.id,
            key=key,
            value=value,
        )


    def log_tag(self, key: str, value: str) -> None:
        run = self._require_active_run()
        self._db_store.save_tag(
            run_id=run.id,
            key=key,
            value=value,
        )