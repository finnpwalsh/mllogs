from datetime import datetime, UTC

import pytest

from sqlalchemy import inspect, insert, select
from sqlalchemy.exc import IntegrityError

from mllogs.new.db import Database
from mllogs.new.db.schema import metadata, experiments, runs


# ==========================
# ----- Initialization -----
# ==========================

def test_create_tables(db):
    inspector = inspect(db.engine)

    assert set(inspector.get_table_names()) == set(
        metadata.tables.keys()
    )


def test_custom_database_path(tmp_path):
    path = tmp_path / "nested" / "test.db"
    database = Database(f"sqlite:///{path}")

    try:
        assert path.exists()
    finally:
        database.close()


def test_in_memory_database():
    database = Database("sqlite:///:memory:")

    try:
        inspector = inspect(database.engine)

        assert set(inspector.get_table_names()) == set(
            metadata.tables.keys()
        )
    finally:
        database.close()


# ========================
# ----- Transactions -----
# ========================

def test_transaction_commit(db, experiment):
    with db.engine.connect() as conn:
        result = conn.execute(
            select(experiments).where(
                experiments.c.id == experiment
            )
        ).mappings().one()

    assert result["id"] == experiment
    assert result["name"] == "test"


def test_transaction_rollback(db):
    with pytest.raises(RuntimeError):
        with db.engine.begin() as conn:
            conn.execute(
                insert(experiments).values(
                    id="exp-001",
                    name="test",
                    created_at=datetime.now(UTC),
                )
            )

            raise RuntimeError("Simulated failure")

    with db.engine.connect() as conn:
        result = conn.execute(
            select(experiments)
        ).mappings().all()

    assert result == []


# =======================
# ----- Constraints -----
# =======================

def test_unique_constraint(db, experiment):
    with pytest.raises(IntegrityError):
        with db.engine.begin() as conn:
            conn.execute(
                insert(experiments).values(
                    id="exp-002",
                    name="test",
                    created_at=datetime.now(UTC),
                )
            )


def test_foreign_key_constraint(db):
    with pytest.raises(IntegrityError):
        with db.engine.begin() as conn:
            conn.execute(
                insert(runs).values(
                    id="run-001",
                    experiment_id="nonexistent",
                    started_at=datetime.now(UTC),
                    status="RUNNING",
                )
            )