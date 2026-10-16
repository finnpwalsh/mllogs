import pandas as pd

from sqlalchemy import Select

from .db import Database
from .db.schema import runs


class Query:
    def __init__(self, db: Database, statement: Select) -> None:
        self._db = db
        self._statement = statement

    def filter(self, column: str, value) -> "Query":
        if column not in runs.c:
            raise ValueError(f"Unknown column: {column}")

        self._statement = self._statement.where(
            runs.c[column] == value
        )
        return self

    def order_by(self, column: str, descending: bool = False) -> "Query":
        if column not in runs.c:
            raise ValueError(f"Unknown column: {column}")

        col = runs.c[column]

        self._statement = self._statement.order_by(
            col.desc() if descending else col.asc()
        )

        return self

    def limit(self, n: int) -> "Query":
        if n < 0:
            raise ValueError("Limit must be non-negative.")

        self._statement = self._statement.limit(n)
        return self

    def to_df(self) -> pd.DataFrame:
        return pd.read_sql(self._statement, self._db.engine)