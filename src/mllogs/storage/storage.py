from .db import DBStore
from .artifacts import ArtifactStore

from mllogs.run import Run
from mllogs.artifact import Artifact


class Storage:
    def __init__(
        self,
        db: DBStore,
        artifact_store: ArtifactStore,
    ) -> None:
        self._db = db
        self._artifact_store = artifact_store

    def save_run(self, run: Run) -> None:
        self._db.save_run(run)

    def load_run(self, run_id: str | None = None) -> Run | None:
        return self._db.load_run(run_id)

    def list_runs(self, limit: int | None = None) -> list[Run]:
        return self._db.list_runs(limit)

    def delete_run(self, run_id: str) -> None:
        self._db.delete_run(run_id)

    def save_artifact(
        self,
        run_id: str,
        artifact: Artifact,
        data: bytes,
    ) -> None:
        self._artifact_store.save(
            run_id=run_id,
            artifact=artifact,
            data=data,
        )
        self._db.save_artifact(
            run_id=run_id,
            artifact=artifact,
        )

    def load_artifact(
        self,
        run_id: str,
        artifact: Artifact,
    ) -> bytes:
        return self._artifact_store.load(
            run_id=run_id,
            artifact=artifact,
        )

    def delete_artifact(
        self,
        run_id: str,
        artifact: Artifact,
    ) -> None:
        self._artifact_store.delete(
            run_id=run_id,
            artifact=artifact,
        )
        self._db.delete_artifact(
            run_id=run_id,
            artifact=artifact,
        )