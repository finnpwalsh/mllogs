import pytest

from mllogs.new.serializers import (
    JoblibSerializer,
    PickleSerializer,
    get_serializer,
    list_serializers,
)


@pytest.mark.parametrize(
    ("format", "serializer_class"),
    [
        ("pkl", PickleSerializer),
        ("joblib", JoblibSerializer),
    ],
)
def test_get_serializer(format, serializer_class):
    serializer = get_serializer(format)

    assert isinstance(serializer, serializer_class)


def test_get_serializer_invalid():
    with pytest.raises(ValueError):
        get_serializer("invalid")


def test_list_serializers():
    assert set(list_serializers()) == {
        "pkl",
        "joblib",
    }