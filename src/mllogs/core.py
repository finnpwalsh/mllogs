from datetime import datetime, UTC
from typing import Any

from .artifact import ArtifactRef
from .query import Query
from .run import Run, RunStatus
from .serializers import get_serializer
from .storage.artifacts import ArtifactStore, LocalArtifactStore
from .storage.db import DBStore, SQLiteStore
from .types import ParamValue


class MLLogs:
    # ======================
    # ----- INITIALIZE -----
    # ======================

    def __init__(
        self,
        db_store: DBStore | None = None,
        artifact_store: ArtifactStore | None = None
    ) -> None:
        self._db_store = db_store if db_store is not None else SQLiteStore()
        self._artifact_store = artifact_store if artifact_store else LocalArtifactStore()

        self._active_run: Run | None = None

        self.query = Query(
            db_store=self._db_store,
            artifact_store=self._artifact_store,
        )


    # ===================
    # ----- HELPERS -----
    # ===================

    def _require_active_run(self) -> Run:
        if self._active_run is None:
            raise RuntimeError("No active run.")

        return self._active_run


    # ===============
    # ----- RUN -----
    # ===============

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


    # ========================
    # ----- RUN METADATA -----
    # ========================

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


    def set_tag(self, key: str, value: str) -> None:
        run = self._require_active_run()
        self._db_store.save_tag(
            run_id=run.id,
            key=key,
            value=value,
        )

    # ====================
    # ----- ARTIFACT -----
    # ====================

    def save_artifact(self, name: str, obj: Any, format: str) -> ArtifactRef:
        run = self._require_active_run()

        artifact_ref = ArtifactRef.create(
            run_id=run.id,
            name=name,
            format=format,
        )
        
        serializer = get_serializer(format)
        data = serializer.serialize(obj)

        self._artifact_store.save(artifact_ref.uri, data)

        # couple artifact + artifact ref stores
        try:
            self._db_store.save_artifact_ref(artifact_ref)
        except Exception:
            self._artifact_store.delete(artifact_ref.uri)
            raise

        return artifact_ref