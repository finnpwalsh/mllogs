from pathlib import Path

from .base import ArtifactStore
from mllogs.artifact import Artifact


class LocalArtifactStore(ArtifactStore):
    def __init__(
        self,
        root_dir: str | Path = ".mllogs/artifacts",
    ) -> None:
        self._root_dir = Path(root_dir)
        self._root_dir.mkdir(parents=True, exist_ok=True)


    def save(
        self,
        run_id: str,
        artifact: Artifact,
        data: bytes,
    ) -> None:
        path = self._root_dir / run_id / artifact.filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


    def load(
        self,
        run_id: str,
        artifact: Artifact,
    ) -> bytes:
        path = self._root_dir / run_id / artifact.filename
        return path.read_bytes()


    def delete(
        self,
        run_id: str,
        artifact: Artifact,
    ) -> None:
        path = self._root_dir / run_id / artifact.filename
        path.unlink()