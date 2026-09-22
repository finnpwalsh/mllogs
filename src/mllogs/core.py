from .storage.db import DBStore, SQLiteStore
from .query import Query
from .tracker import Tracker


class MLLogs:
    def __init__(self, db_store: DBStore | None = None):
        db = db_store if db_store is not None else SQLiteStore()
        self.query = Query(db)
        self.tracker = Tracker(db)