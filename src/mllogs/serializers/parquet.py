import io

import pandas as pd

from .base import Serializer


class ParquetSerializer(Serializer):
    def serialize(self, obj: pd.DataFrame) -> bytes:
        buffer = io.BytesIO()
        obj.to_parquet(buffer)
        return buffer.getvalue()

    def deserialize(self, data: bytes) -> pd.DataFrame:
        buffer = io.BytesIO(data)
        return pd.read_parquet(buffer)