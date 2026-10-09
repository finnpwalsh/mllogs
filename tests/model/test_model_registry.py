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

@pytest.fixture
def registered_model(registry):
    return registry.register_model("credit-risk")

def test_register_model(registered_model):
    assert registered_model.name == "credit-risk"

def test_register_model_is_idempotent(registry):
    first = registry.register_model("credit-risk")
    second = registry.register_model("credit-risk")

    assert second == first


# =========================
# ----- MODEL VERSION -----
# =========================

@pytest.fixture
def version(registry, registered_model, artifact_ref):
    return registry.create_version(
        model_name=registered_model.name,
        artifact_ref=artifact_ref,
    )

def test_create_first_version(version, artifact_ref):
    assert version.version == 1
    assert version.artifact_id == artifact_ref.id

def test_create_version_increments(registry, version, artifact_ref):
    first = version

    second = registry.create_version(
        model_name="credit-risk",
        artifact_ref=artifact_ref,
    )

    assert first.version == 1
    assert second.version == 2

def test_create_version_reuses_registered_model(registry, version, artifact_ref):
    first = version

    second = registry.create_version(
        model_name="credit-risk",
        artifact_ref=artifact_ref,
    )

    assert first.model_id == second.model_id

def test_version_round_trip(registry, version):
    assert registry.get_version(model_name="credit-risk", version=1) == version

def test_get_latest_version(registry, artifact_ref):
    registry.create_version("credit-risk", artifact_ref)
    latest = registry.create_version("credit-risk", artifact_ref)

    loaded = registry.get_latest_version("credit-risk")

    assert loaded == latest

def test_create_version_auto_registers_model(version, registered_model, store):
    model = store.load_registered_model_by_name(registered_model.name)

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


# =======================
# ----- MODEL ALIAS -----
# =======================

@pytest.fixture
def alias(registry, version):
    return registry.set_alias(version, "champion")

def test_set_alias(alias, version):
    assert alias.model_id == version.model_id
    assert alias.version_id == version.id
    assert alias.name == "champion"

def test_alias_round_trip(registry, registered_model, alias):
    assert registry.get_alias(registered_model.name, alias.name) == alias

def test_set_alias_updates_version(registry, artifact_ref):
    first = registry.create_version("credit-risk", artifact_ref)
    second = registry.create_version("credit-risk", artifact_ref)

    original = registry.set_alias(first, "champion")
    updated = registry.set_alias(second, "champion")

    assert updated.version_id == second.id
    assert updated.id == original.id

    assert registry.get_alias("credit-risk", "champion") == updated

def test_aliases_scoped_to_model(registry, artifact_ref):
    credit = registry.create_version("credit-risk", artifact_ref)
    inflation = registry.create_version("inflation-model", artifact_ref)

    credit_alias = registry.set_alias(credit, "champion")
    inflation_alias = registry.set_alias(inflation, "champion")

    assert credit_alias.id != inflation_alias.id
    assert credit_alias.version_id == credit.id
    assert inflation_alias.version_id == inflation.id

def test_set_alias_is_idempotent(registry, artifact_ref):
    version = registry.create_version("credit-risk", artifact_ref)

    first = registry.set_alias(version, "champion")
    second = registry.set_alias(version, "champion")

    assert first == second

def test_get_version_by_alias(registry, artifact_ref):
    version = registry.create_version("credit-risk", artifact_ref)
    registry.set_alias(version, "champion")

    loaded = registry.get_version_by_alias("credit-risk", "champion")

    assert loaded == version

def test_get_version_by_alias_after_reassignment(registry, artifact_ref):
    first = registry.create_version("credit-risk", artifact_ref)
    second = registry.create_version("credit-risk", artifact_ref)

    registry.set_alias(first, "champion")
    registry.set_alias(second, "champion")

    loaded = registry.get_version_by_alias("credit-risk", "champion")

    assert loaded == second


# --- Errors ---

def test_get_missing_alias_raises(registry):
    with pytest.raises(KeyError):
        registry.get_alias("credit-risk", "champion")

def test_get_version_by_alias_missing_raises(registry):
    with pytest.raises(KeyError):
        registry.get_version_by_alias("credit-risk", "champion")