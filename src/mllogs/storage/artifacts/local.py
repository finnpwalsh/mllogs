from pathlib import Path

from .base import ArtifactStore


class LocalArtifactStore(ArtifactStore):
    def __init__(self, root_dir: str | Path = ".mllogs") -> None:
        self._root_dir = Path(root_dir)
        self._artifact_dir = self._root_dir / "artifacts"


    def save(self, uri: str, data: bytes) -> None:
        path = self._artifact_dir / uri

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


    def load(self, uri: str) -> bytes:
        path = self._artifact_dir / uri
        return path.read_bytes()


    def delete(self, uri: str) -> None:
        path = self._artifact_dir / uri
        path.unlink()