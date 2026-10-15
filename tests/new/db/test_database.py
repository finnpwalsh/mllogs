
import pytest

from sqlalchemy import inspect, insert, select
from sqlalchemy.exc import IntegrityError

from mllogs.new.db import Database
from mllogs.new.db.schema import metadata, experiments, runs


# ==========================
# ----- Initialization -----
# ==========================
# Database creation and configuration

def test_create_tables(db):
    inspector = inspect(db.engine)

    assert set(inspector.get_table_names()) == set(
        metadata.tables.keys()
    )


def test_custom_database_path(tmp_path):
    path = tmp_path / "nested" / "test.db"
    db = Database(f"sqlite:///{path}")

    try:
        assert path.exists()
    finally:
        db.close()


def test_in_memory_database():
    db = Database("sqlite:///:memory:")

    try:
        inspector = inspect(db.engine)
        assert set(inspector.get_table_names()) == set(
            metadata.tables.keys()
        )
    finally:
        db.close()


# ========================
# ----- Transactions -----
# ========================
# Reading, committing, and rolling back

def test_insert_and_select(db):
    with db.engine.begin() as conn:
        conn.execute(
            insert(experiments).values(
                id="exp-001",
                name="test",
                created_at="2026-10-15T12:00:00",
            )
        )

    with db.engine.connect() as conn:
        result = conn.execute(
            select(experiments).where(
                experiments.c.id == "exp-001"
            )
        ).mappings().one()

    assert result["name"] == "test"


def test_transaction_commit(db):
    with db.engine.begin() as conn:
        conn.execute(
            insert(experiments).values(
                id="exp-001",
                name="test",
                created_at="2026-10-15T12:00:00",
            )
        )

    with db.engine.connect() as conn:
        result = conn.execute(select(experiments)).mappings().all()

    assert len(result) == 1


def test_transaction_rollback(db):
    with pytest.raises(RuntimeError):
        with db.engine.begin() as conn:
            conn.execute(
                insert(experiments).values(
                    id="exp-001",
                    name="test",
                    created_at="2026-10-15T12:00:00",
                )
            )
            raise RuntimeError("Simulated failure")

    with db.engine.connect() as conn:
        result = conn.execute(select(experiments)).mappings().all()

    assert result == []


# =======================
# ----- Constraints -----
# =======================
# Data integrity

def test_unique_constraint(db):
    with db.engine.begin() as conn:
        conn.execute(
            insert(experiments).values(
                id="exp-001",
                name="test",
                created_at="2026-10-15T12:00:00",
            )
        )

    with pytest.raises(IntegrityError):
        with db.engine.begin() as conn:
            conn.execute(
                insert(experiments).values(
                    id="exp-002",
                    name="test",
                    created_at="2026-10-15T12:00:00",
                )
            )


def test_foreign_key_constraint(db):
    with pytest.raises(IntegrityError):
        with db.engine.begin() as conn:
            conn.execute(
                insert(runs).values(
                    id="run-001",
                    experiment_id="nonexistent",
                    started_at="2026-10-15T12:00:00",
                    status="RUNNING",
                )
            )