from sqlalchemy import Select, select

from .base import Query
from mllogs.storage.db import Database
from mllogs.storage.db.schema import runs, params, metrics, tags


class RunsQuery(Query):
    def __init__(self, db: Database, statement: Select | None = None) -> None:
        stmt = statement if statement is not None else select(runs)

        with db.engine.connect() as conn:
            for namespace, table in (
                ("params", params),
                ("metrics", metrics),
                ("tags", tags),
            ):
                keys = conn.execute(
                    select(table.c.key).distinct()
                ).scalars().all()

                for key in keys:
                    value = (
                        select(table.c.value)
                        .where(
                            table.c.run_id == runs.c.id,
                            table.c.key == key,
                        )
                        .correlate(runs)
                        .scalar_subquery()
                    )

                    stmt = stmt.add_columns(
                        value.label(f"{namespace}.{key}")
                    )

        super().__init__(db, stmt)