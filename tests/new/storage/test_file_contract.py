import pytest

from mllogs.new.storage.files import FileStore, LocalFileStore


FILE_STORES = [
    LocalFileStore,
]


@pytest.fixture(params=FILE_STORES)
def store(request, tmp_path) -> FileStore:
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

