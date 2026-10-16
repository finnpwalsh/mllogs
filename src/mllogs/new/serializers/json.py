import json
from typing import Any

from .base import Serializer


class JSONSerializer(Serializer):
    def serialize(self, obj: Any) -> bytes:
        return json.dumps(obj).encode("utf-8")

    def deserialize(self, data: bytes) -> Any:
        return json.loads(data.decode("utf-8"))