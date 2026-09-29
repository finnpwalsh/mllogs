from datetime import datetime, UTC
import pytest

from mllogs.artifact import ArtifactRef
from mllogs.run import Run, RunStatus
from mllogs.storage.db import SQLiteStore


# ================
# --- Fixtures ---
# ================


@pytest.fixture()
def store(tmp_path):
    return SQLiteStore(tmp_path / "mllogs.db")


@pytest.fixture
def run():
    return Run(
        id="run-123",
        started_at=datetime.now(UTC),
        status=RunStatus.COMPLETE,
        ended_at=datetime.now(UTC),
    )


@pytest.fixture
def artifact_ref():
    return ArtifactRef.create(
        run_id="run-123",
        name="model",
        format="joblib",
    )


# ===========================
# ----- SQLITE CONTRACT -----
# ===========================

def test_delete_run_cascades_child_rows(store, run, artifact_ref):
    store.save_run(run)
    
    store.save_param(run.id, "alpha", 0.1)
    store.save_metric(run.id, "accuracy", 0.95)
    store.save_tag(run.id, "model", "linear")
    store.save_artifact_ref(artifact_ref)

    store.delete_run(run.id)

    for table in ("params", "metrics", "tags", "artifacts"):
        row = store._connection.execute(
            f"""
            SELECT COUNT(*) AS count
            FROM {table}
            WHERE run_id = ?
            """,
            (run.id,),
        ).fetchone()

        assert row["count"] == 0