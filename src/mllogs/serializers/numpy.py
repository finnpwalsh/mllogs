import io

import numpy as np

from .base import Serializer


class NumpySerializer(Serializer):
    def serialize(self, obj: np.ndarray) -> bytes:
        buffer = io.BytesIO()
        np.save(buffer, obj, allow_pickle=False)
        return buffer.getvalue()

    def deserialize(self, data: bytes) -> np.ndarray:
        buffer = io.BytesIO(data)
        return np.load(buffer, allow_pickle=False)