import pandas as pd
import pytest


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