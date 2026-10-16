from abc import ABC, abstractmethod
from typing import Any, Self

import pandas as pd

from sqlalchemy import Select
from sqlalchemy.sql.elements import ColumnElement

from ..db import Database


class Query(ABC):
    # ======================
    # ----- Initialize -----
    # ======================

    def __init__(self, db: Database, statement: Select) -> None:
        self._db = db
        self._statement = statement


    # ===================
    # ----- Helpers -----
    # ===================

    def _resolve_column(self, name) -> ColumnElement[Any]:
        try:
            return self._statement.selected_columns[name]
        except KeyError:
            raise ValueError(f"Unknown column: {name}") from None


    # ===================
    # ----- Methods -----
    # ===================

    def filter(self, column: str, value: Any) -> Self:
        col = self._resolve_column(column)
        self._statement = self._statement.where(col == value)
        return self

    def order_by(self, column: str, descending: bool = False) -> Self:
        col = self._resolve_column(column)

        self._statement = self._statement.order_by(
            col.desc() if descending else col.asc()
        )
        return self

    def limit(self, n: int) -> Self:
        if n < 0:
            raise ValueError("Limit must be non-negative.")

        self._statement = self._statement.limit(n)
        return self

    def to_df(self) -> pd.DataFrame:
        return pd.read_sql(self._statement, self._db.engine)