from .db import DBStore
from .files import FileStore

from mllogs.run import Run


class Storage:
    def __init__(
        self,
        db: DBStore,
        file: FileStore,
    ) -> None:
        self._db = db
        self._file = file

    def save_run(self, run: Run) -> None:
        self._db.save_run(run)

    def load_run(self, run_id: str | None = None) -> Run | None:
        return self._db.load_run(run_id)

    def list_runs(self, limit: int | None = None) -> list[Run]:
        return self._db.list_runs(limit)

    def delete_run(self, run_id: str) -> None:
        self._db.delete_run(run_id)