from abc import ABC, abstractmethod


class FileStore(ABC):
    @abstractmethod
    def save(
        self,
        uri: str,
        data: bytes,
    ) -> str:
        """
        Saves a file and returns its URI.
        """
        ...

    @abstractmethod
    def load(self, uri: str) -> bytes:
        """
        Returns the stored file.
        """
        ...

    @abstractmethod
    def delete(self, uri: str) -> None:
        """
        Deletes a stored file.
        """
        ...