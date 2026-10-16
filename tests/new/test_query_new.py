
import pandas as pd
import pytest

from sqlalchemy import select

from mllogs.new.query import Query
from mllogs.new.db.schema import runs


@pytest.fixture
def query(db, sample_runs):
    return Query(db, select(runs))


# =====================
# ----- Filtering -----
# =====================

def test_filter(query):
    df = query.filter("status", "COMPLETE").to_df()

    assert set(df["id"]) == {"run-001", "run-003"}

def test_invalid_filter(query):
    with pytest.raises(ValueError):
        query.filter("unknown", "value")


# ====================
# ----- Ordering -----
# ====================

def test_order_by_ascending(query):
    df = query.order_by("started_at").to_df()

    assert df["id"].tolist() == [
        "run-001",
        "run-002",
        "run-003",
    ]

def test_order_by_descending(query):
    df = query.order_by(
        "started_at",
        descending=True,
    ).to_df()

    assert df["id"].tolist() == [
        "run-003",
        "run-002",
        "run-001",
    ]

def test_invalid_order_by(query):
    with pytest.raises(ValueError):
        query.order_by("unknown")


# ====================
# ----- Limiting -----
# ====================

def test_limit(query):
    df = query.order_by("started_at").limit(2).to_df()

    assert df["id"].tolist() == ["run-001", "run-002"]

def test_invalid_limit(query):
    with pytest.raises(ValueError):
        query.limit(-1)


# =========================
# ----- DataFrames -----
# =========================

def test_to_df(query):
    df = query.to_df()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3

def test_query_chaining(query):
    df = (
        query
        .filter("status", "COMPLETE")
        .order_by("started_at", descending=True)
        .limit(1)
        .to_df()
    )

    assert df["id"].tolist() == ["run-003"]