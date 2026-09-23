import pytest

from mllogs.storage.artifacts import ArtifactStore, LocalArtifactStore


ARTIFACT_STORES = [
    LocalArtifactStore,
]


@pytest.fixture(params=ARTIFACT_STORES)
def store(request, tmp_path) -> ArtifactStore:
    store_class = request.param
    return store_class(tmp_path)


def test_save(store, tmp_path):
    store.save("run-123/model.pkl", b"model-data")

    path = tmp_path / "artifacts" / "run-123" / "model.pkl"

    assert path.exists()
    assert path.read_bytes() == b"model-data"


def test_load(store):
    store.save("run-123/model.pkl", b"model-data")
    assert store.load("run-123/model.pkl") == b"model-data"


def test_delete(store, tmp_path):
    store.save("run-123/model.pkl", b"model-data")
    store.delete("run-123/model.pkl")

    path = tmp_path / "artifacts" / "run-123" / "model.pkl"

    assert not path.exists()

