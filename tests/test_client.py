import pandas as pd
import pytest

from sqlalchemy import select

from mllogs.storage.db.schema import runs, params, metrics, tags


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


# ========================
# ----- Run Metadata -----
# ========================


# --- Params ---

@pytest.mark.parametrize(
    "value",
    [0.1, 100, "adam", True, None],
)
def test_log_param(mll, value):
    mll.create_experiment("test")

    with mll.run("test"):
        mll.log_param("parameter", value)

    with mll._db.engine.connect() as conn:
        result = conn.execute(
            select(params.c.value)
        ).scalar_one()

    assert result == value
    assert type(result) is type(value)


# --- Metrics ---

def test_log_metric(mll):
    mll.create_experiment("test")

    with mll.run("test"):
        mll.log_metric("accuracy", 0.95)

    with mll._db.engine.connect() as conn:
        result = conn.execute(
            select(metrics.c.value)
        ).scalar_one()

    assert result == pytest.approx(0.95)


# --- Tags ---

def test_set_tag(mll):
    mll.create_experiment("test")

    with mll.run("test"):
        mll.set_tag("dataset", "diabetes")

    with mll._db.engine.connect() as conn:
        result = conn.execute(
            select(tags.c.value)
        ).scalar_one()

    assert result == "diabetes"


# --- All ---

def test_log_metadata_without_run(mll):
    with pytest.raises(RuntimeError, match="No active run"):
        mll.log_param("alpha", 0.1)

    with pytest.raises(RuntimeError, match="No active run"):
        mll.log_metric("accuracy", 0.95)

    with pytest.raises(RuntimeError, match="No active run"):
        mll.set_tag("dataset", "diabetes")


# ========================
# ----- Model Saving -----
# ========================

def test_model_round_trip(mll):
    model = {"weights": [0.1, 0.2, 0.3]}

    mll.create_experiment("test")

    with mll.run("test") as run_id:
        mll.save_model(model)

    saved = mll.load_model(run_id)
    assert model == saved

    # Verify saved model
    path = mll._files._root / f"{run_id}.joblib"
    assert path.exists()


def test_save_model_without_active_run(mll):
    with pytest.raises(RuntimeError, match="No active run"):
        mll.save_model({"weights": [1, 2, 3]})


def test_save_model_twice(mll):
    mll.create_experiment("test")

    with mll.run("test"):
        mll.save_model({"weights": [1, 2, 3]})

        with pytest.raises(ValueError, match="already been saved"):
            mll.save_model({"weights": [4, 5, 6]})


def test_save_model_with_pickle(mll):
    mll.create_experiment("test")

    with mll.run("test") as run_id:
        mll.save_model({"weights": [1, 2, 3]}, format="pkl")

    with mll._db.engine.connect() as conn:
        model_format = conn.execute(
            select(runs.c.model_format)
            .where(runs.c.id == run_id)
        ).scalar_one()

    assert model_format == "pkl"
