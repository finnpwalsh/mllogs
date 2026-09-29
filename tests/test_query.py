from unittest.mock import Mock

import pytest

from mllogs.artifact import ArtifactRef
from mllogs.query import Query


@pytest.fixture
def artifact_refs():
    return [
        ArtifactRef.create(
            run_id="run-123",
            name="model",
            format="joblib",
        ),
        ArtifactRef.create(
            run_id="run-123",
            name="predictions",
            format="csv",
        ),
    ]


def test_list_artifacts(artifact_refs):
    db_store=Mock()
    artifact_store=Mock()


    db_store.load_artifact_refs.return_value = artifact_refs

    query = Query(
        db_store=db_store,
        artifact_store=artifact_store,
    )

    result = query.list_artifacts("run-123")

    assert result == [ref.name for ref in artifact_refs]