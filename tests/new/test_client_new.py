import pandas as pd
import pytest


# =======================
# ----- Experiments -----
# =======================

def test_experiment_round_trip(mll):
    result = mll.create_experiment("ridge-tuning")

    df = mll.experiments()

    assert result is None
    assert len(df) == 1
    assert df.iloc[0]["name"] == "ridge-tuning"
    assert pd.notna(df.iloc[0]["id"])
    assert pd.notna(df.iloc[0]["created_at"])


def test_delete_experiment(mll):
    mll.create_experiment("ridge-tuning")
    mll.delete_experiment("ridge-tuning")

    assert mll.experiments().empty


# ================
# ----- Runs -----
# ================

def test_run_complete(mll):
    mll.create_experiment("ridge-tuning")

    with mll.run("ridge-tuning"):
        pass

    df = mll.runs("ridge-tuning").to_df()

    assert len(df) == 1
    assert df.iloc[0]["status"] == "COMPLETE"
    assert pd.notna(df.iloc[0]["started_at"])
    assert pd.notna(df.iloc[0]["ended_at"])


def test_run_failed(mll):
    mll.create_experiment("ridge-tuning")

    with pytest.raises(ValueError, match="Training failed"):
        with mll.run("ridge-tuning"):
            raise ValueError("Training failed")

    df = mll.runs("ridge-tuning").to_df()

    assert len(df) == 1
    assert df.iloc[0]["status"] == "FAILED"
    assert pd.notna(df.iloc[0]["ended_at"])


def test_run_requires_experiment(mll):
    with pytest.raises(ValueError, match="Experiment not found"):
        with mll.run("nonexistent"):
            pass

    assert mll.runs().to_df().empty


def test_run_active_status(mll):
    mll.create_experiment("ridge-tuning")

    with mll.run("ridge-tuning"):
        df = mll.runs("ridge-tuning").to_df()

        assert len(df) == 1
        assert df.iloc[0]["status"] == "RUNNING"
        assert pd.isna(df.iloc[0]["ended_at"])


def test_nested_runs_rejected(mll):
    mll.create_experiment("ridge-tuning")

    with mll.run("ridge-tuning"):
        with pytest.raises(RuntimeError, match="already active"):
            with mll.run("ridge-tuning"):
                pass

    df = mll.runs("ridge-tuning").to_df()

    assert len(df) == 1
    assert df.iloc[0]["status"] == "COMPLETE"


def test_sequential_runs(mll):
    mll.create_experiment("ridge-tuning")

    with mll.run("ridge-tuning"):
        pass

    with mll.run("ridge-tuning"):
        pass

    df = mll.runs("ridge-tuning").to_df()

    assert len(df) == 2
    assert set(df["status"]) == {"COMPLETE"}
    assert df["id"].nunique() == 2