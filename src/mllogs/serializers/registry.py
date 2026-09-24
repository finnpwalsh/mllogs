from .base import Serializer
from .csv import CSVSerializer
from .joblib import JoblibSerializer
from .json import JSONSerializer
from .parquet import ParquetSerializer
from .pickle import PickleSerializer
from .numpy import NumpySerializer


SERIALIZERS: dict[str, Serializer] = {
    "csv": CSVSerializer(),
    "joblib": JoblibSerializer(),
    "json": JSONSerializer(),
    "parquet": ParquetSerializer(),
    "pkl": PickleSerializer(),
    "npy": NumpySerializer(),
}


def get_serializer(format: str) -> Serializer:
    try:
        return SERIALIZERS[format]
    except KeyError:
        raise ValueError(f"Unsupported serializer format: {format}")


def list_serializers() -> list[str]:
    return list(SERIALIZERS)