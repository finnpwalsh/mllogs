from .base import Serializer
from .joblib import JoblibSerializer
from .pickle import PickleSerializer


_SERIALIZERS: dict[str, Serializer] = {
    "joblib": JoblibSerializer(),
    "pkl": PickleSerializer(),
}


def get_serializer(format: str) -> Serializer:
    try:
        return _SERIALIZERS[format]
    except KeyError:
        raise ValueError(f"Unsupported serializer format: {format}")


def list_serializers() -> list[str]:
    return list(_SERIALIZERS)