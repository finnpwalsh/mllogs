import pickle
from typing import Any

from .base import Serializer


class PickleSerializer(Serializer):
    def serialize(self, obj: Any) -> bytes:
        return pickle.dumps(obj)

    def deserialize(self, data: bytes) -> Any:
        return pickle.loads(data)