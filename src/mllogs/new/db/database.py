
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine, make_url

from .schema import metadata


class Database:
    def __init__(
        self,
        url: str = "sqlite:///.mllogs/mllogs.db",
    ) -> None:
        db_url = make_url(url)

        if db_url.get_backend_name() == "sqlite":
            self._configure_sqlite(db_url)

        self.engine: Engine = create_engine(db_url)

        if db_url.get_backend_name() == "sqlite":
            self._enable_sqlite_foreign_keys()

        metadata.create_all(self.engine)

    def _configure_sqlite(self, url: URL) -> None:
        if url.database and url.database != ":memory:":
            Path(url.database).parent.mkdir(
                parents=True,
                exist_ok=True,
            )

    def _enable_sqlite_foreign_keys(self) -> None:
        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(dbapi_connection, connection_record):
            autocommit = getattr(dbapi_connection, "autocommit", None)

            if autocommit is not None:
                dbapi_connection.autocommit = True

            try:
                cursor = dbapi_connection.cursor()
                try:
                    cursor.execute("PRAGMA foreign_keys = ON")
                finally:
                    cursor.close()
            finally:
                if autocommit is not None:
                    dbapi_connection.autocommit = autocommit

    def close(self) -> None:
        self.engine.dispose()