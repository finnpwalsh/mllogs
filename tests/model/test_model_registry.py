import pytest

from mllogs.storage.db import SQLiteStore
from mllogs.model.registry import ModelRegistry
from mllogs.artifact import ArtifactRef
from mllogs.run import Run


# ====================
# ----- FIXTURES -----
# ====================

@pytest.fixture()
def store(tmp_path):
    return SQLiteStore(tmp_path / "mllogs.db")

@pytest.fixture()
def registry(store):
    return ModelRegistry(store)

@pytest.fixture()
def run(store):
    run = Run.create()
    store.save_run(run)
    return run


@pytest.fixture()
def artifact_ref(store, run):
    ref = ArtifactRef.create(
        run_id=run.id,
        name="model",
        format="joblib",
    )
    store.save_artifact_ref(ref)
    return ref


# ============================
# ----- REGISTERED MODEL -----
# ============================

def test_register_model(registry):
    model = registry.register_model("credit-risk")
    assert model.name == "credit-risk"

def test_register_model_is_idempotent(registry):
    first = registry.register_model("credit-risk")
    second = registry.register_model("credit-risk")

    assert second == first


# =========================
# ----- MODEL VERSION -----
# =========================

def test_create_first_version(registry, artifact_ref):
    version = registry.create_version(
        model_name="credit-risk",
        artifact_ref=artifact_ref,
    )

    assert version.version == 1
    assert version.artifact_id == artifact_ref.id

def test_create_version_increments(registry, artifact_ref):
    first = registry.create_version(
        model_name="credit-risk",
        artifact_ref=artifact_ref,
    )

    second = registry.create_version(
        model_name="credit-risk",
        artifact_ref=artifact_ref,
    )

    assert first.version == 1
    assert second.version == 2

def test_create_version_reuses_registered_model(registry, artifact_ref):
    first = registry.create_version(
        model_name="credit-risk",
        artifact_ref=artifact_ref,
    )

    second = registry.create_version(
        model_name="credit-risk",
        artifact_ref=artifact_ref,
    )

    assert first.model_id == second.model_id

def test_version_round_trip(registry, artifact_ref):
    created = registry.create_version(
        model_name="credit-risk",
        artifact_ref=artifact_ref,
    )

    loaded = registry.get_version(
        model_name="credit-risk",
        version=1,
    )

    assert loaded == created

def test_get_latest_version(registry, artifact_ref):
    registry.create_version("credit-risk", artifact_ref)
    latest = registry.create_version("credit-risk", artifact_ref)

    loaded = registry.get_latest_version("credit-risk")

    assert loaded == latest

def test_create_version_auto_registers_model(registry, artifact_ref, store):
    version = registry.create_version(
        model_name="credit-risk",
        artifact_ref=artifact_ref,
    )

    model = store.load_registered_model_by_name("credit-risk")

    assert model.id == version.model_id


# --- Errors ---

def test_get_version_missing_version_raises(registry, artifact_ref):
    registry.create_version("credit-risk", artifact_ref)

    with pytest.raises(KeyError):
        registry.get_version(
            model_name="credit-risk",
            version=2,
        )

def test_get_latest_version_without_versions_raises(registry):
    registry.register_model("credit-risk")

    with pytest.raises(KeyError):
        registry.get_latest_version("credit-risk")