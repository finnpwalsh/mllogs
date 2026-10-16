import pandas as pd
import pytest

from mllogs.storage.db.schema import params, metrics


# ===========================
# ----- Run Flattening -----
# ===========================

def test_runs_flattening(runs_query):
    df = runs_query.to_df()

    assert len(df) == 3

    df = df.set_index("id")

    assert df.loc["run-001", "params.alpha"] == 0.1
    assert df.loc["run-002", "params.alpha"] == 1.0
    assert pd.isna(df.loc["run-003", "params.alpha"])

    assert df.loc["run-001", "metrics.mse"] == pytest.approx(0.45)
    assert df.loc["run-002", "metrics.mse"] == pytest.approx(0.38)
    assert df.loc["run-003", "metrics.mse"] == pytest.approx(0.42)

    assert df.loc["run-001", "tags.dataset"] == "diabetes"
    assert pd.isna(df.loc["run-002", "tags.dataset"])


# ==============================
# ----- Metric Ordering -----
# ==============================

def test_order_by_metric(runs_query):
    df = (
        runs_query
        .order_by("metrics.mse")
        .limit(2)
        .to_df()
    )

    assert df["id"].tolist() == ["run-002", "run-003"]


def test_order_by_metric_descending(runs_query):
    df = (
        runs_query
        .order_by("metrics.mse", descending=True)
        .limit(2)
        .to_df()
    )

    assert df["id"].tolist() == ["run-001", "run-003"]


# ===============================
# ----- Metric Filtering -----
# ===============================

def test_filter_by_metric(runs_query):
    df = runs_query.filter("metrics.mse", 0.38).to_df()

    assert df["id"].tolist() == ["run-002"]


# =================================
# ----- Parameter Filtering -----
# =================================

def test_filter_by_param(runs_query):
    df = runs_query.filter("params.alpha", 0.1).to_df()

    assert df["id"].tolist() == ["run-001"]


# ===========================
# ----- Tag Filtering -----
# ===========================

def test_filter_by_tag(runs_query):
    df = runs_query.filter("tags.dataset", "diabetes").to_df()

    assert df["id"].tolist() == ["run-001"]


# ===========================
# ----- Query Chaining -----
# ===========================

def test_runs_query_chaining(runs_query):
    df = (
        runs_query
        .filter("status", "COMPLETE")
        .order_by("metrics.mse")
        .limit(1)
        .to_df()
    )

    assert df["id"].tolist() == ["run-003"]



# ==================================
# ----- Unqualified Columns -----
# ==================================

def test_order_by_unqualified_metric(runs_query):
    df = (
        runs_query
        .order_by("mse")
        .limit(2)
        .to_df()
    )

    assert df["id"].tolist() == ["run-002", "run-003"]


def test_order_by_unqualified_metric_descending(runs_query):
    df = (
        runs_query
        .order_by("mse", descending=True)
        .limit(2)
        .to_df()
    )

    assert df["id"].tolist() == ["run-001", "run-003"]


def test_filter_by_unqualified_metric(runs_query):
    df = runs_query.filter("mse", 0.38).to_df()

    assert df["id"].tolist() == ["run-002"]


def test_filter_by_unqualified_param(runs_query):
    df = runs_query.filter("alpha", 0.1).to_df()

    assert df["id"].tolist() == ["run-001"]


def test_filter_by_unqualified_tag(runs_query):
    df = runs_query.filter("dataset", "diabetes").to_df()

    assert df["id"].tolist() == ["run-001"]


def test_invalid_unqualified_column(runs_query):
    with pytest.raises(ValueError, match="Unknown column"):
        runs_query.filter("nonexistent", 1)


# ==============================
# ----- Query Chaining -----
# ==============================

def test_unqualified_query_chaining(runs_query):
    df = (
        runs_query
        .filter("status", "COMPLETE")
        .order_by("mse")
        .limit(1)
        .to_df()
    )

    assert df["id"].tolist() == ["run-003"]


# ================================
# ----- Ambiguous Columns -----
# ================================

def test_ambiguous_column(db, sample_runs):
    from mllogs.query import RunsQuery

    with db.engine.begin() as conn:
        conn.execute(
            params.insert().values(
                run_id="run-001",
                key="score",
                value=0.5,
            )
        )
        conn.execute(
            metrics.insert().values(
                run_id="run-001",
                key="score",
                value=0.8,
            )
        )

    query = RunsQuery(db)

    with pytest.raises(ValueError, match="Ambiguous column"):
        query.order_by("score")


def test_qualified_ambiguous_columns(db, sample_runs):
    from mllogs.query import RunsQuery

    with db.engine.begin() as conn:
        conn.execute(
            params.insert().values(
                run_id="run-001",
                key="score",
                value=0.5,
            )
        )
        conn.execute(
            metrics.insert().values(
                run_id="run-001",
                key="score",
                value=0.8,
            )
        )

    query = RunsQuery(db)

    param_df = query.filter("params.score", 0.5).to_df()

    assert param_df["id"].tolist() == ["run-001"]

    query = RunsQuery(db)

    metric_df = query.filter("metrics.score", 0.8).to_df()

    assert metric_df["id"].tolist() == ["run-001"]