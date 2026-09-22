from .run import Run
from .types import ParamValue
from .storage.db import DBStore


class Query:
    def __init__(self, db_store: DBStore) -> None:
        self._db_store = db_store

    def get_run(self, run_id: str) -> Run:
        return self._db_store.load_run(run_id)

    def get_params(self, run_id: str) -> dict[str, ParamValue]:
        return self._db_store.load_params(run_id)

    def get_metrics(self, run_id: str) -> dict[str, float]:
        return self._db_store.load_metrics(run_id)

    def get_tags(self, run_id: str) -> dict[str, str]:
        return self._db_store.load_tags(run_id)