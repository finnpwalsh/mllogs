import pytest

from mllogs.new.serializers import (
    JoblibSerializer,
    PickleSerializer,
)


def assert_equal(a, b):
    assert a == b


@pytest.mark.parametrize(
        ("serializer", "obj", "assertion"),
        [
            (
                PickleSerializer(),
                {"alpha": 0.1},
                assert_equal,
            ),
            (
                JoblibSerializer(),
                {"alpha": 0.1},
                assert_equal,
            ),
        ],
)


def test_round_trip(serializer, obj, assertion):
    data = serializer.serialize(obj)
    result = serializer.deserialize(data)

    assert isinstance(data, bytes)
    assertion(result, obj)