import numpy as np
import pandas as pd
import pytest

from mllogs.serializers import (
    CSVSerializer,
    JoblibSerializer,
    JSONSerializer,
    NumpySerializer,
    ParquetSerializer,
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
            (
                JSONSerializer(),
                {"alpha": 0.1},
                assert_equal,
            ),
            (
                CSVSerializer(),
                pd.DataFrame({"x": [1, 2, 3]}),
                pd.testing.assert_frame_equal,
            ),
            (
                ParquetSerializer(),
                pd.DataFrame({"x": [1, 2, 3]}),
                pd.testing.assert_frame_equal,
            ),
            (
                NumpySerializer(),
                np.array([1, 2, 3]),
                np.testing.assert_array_equal,
            ),
        ],
)


def test_round_trip(serializer, obj, assertion):
    data = serializer.serialize(obj)
    result = serializer.deserialize(data)

    assert isinstance(data, bytes)
    assertion(result, obj)