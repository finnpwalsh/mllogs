import io
from typing import Any

import joblib

from .base import Serializer


class JoblibSerializer(Serializer):
    def serialize(self, obj: Any) -> bytes:
        buffer = io.BytesIO()
        joblib.dump(obj, buffer)
        return buffer.getvalue()

    def deserialize(self, data: bytes) -> Any:
        buffer = io.BytesIO(data)
        return joblib.load(buffer)