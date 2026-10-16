import io

import pandas as pd

from .base import Serializer


class CSVSerializer(Serializer):
    def serialize(self, obj: pd.DataFrame) -> bytes:
        return obj.to_csv(index=False).encode("utf-8")

    def deserialize(self, data: bytes) -> pd.DataFrame:
        return pd.read_csv(io.BytesIO(data))