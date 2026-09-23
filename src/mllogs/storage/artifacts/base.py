from abc import ABC, abstractmethod


class ArtifactStore(ABC):
    @abstractmethod
    def save(self, uri: str, data: bytes) -> None:
        ...

    @abstractmethod
    def load(self, uri: str) -> bytes:
        ...

    @abstractmethod
    def delete(self, uri: str) -> None:
        ...