from abc import ABC, abstractmethod
from typing import Any


class Serializer(ABC):
    @abstractmethod
    def serialize(self, obj: Any) -> bytes:
        ...

    @abstractmethod
    def deserialize(self, data: bytes) -> Any:
        ...