from abc import ABC, abstractmethod

from mllogs.run import Artifact


class ArtifactStore(ABC):
    @abstractmethod
    def save(
        self,
        run_id: str,
        artifact: Artifact,
        data: bytes
    ) -> None:
        """
        Saves an artifact.
        """
        ...

    @abstractmethod
    def load(
        self,
        run_id: str,
        artifact: Artifact,
    ) -> bytes:
        """
        Returns the stored file.
        """
        ...

    @abstractmethod
    def delete(
        self,
        run_id: str,
        artifact: Artifact,
    ) -> None:
        """
        Deletes a stored file.
        """
        ...