from dataclasses import dataclass
from datetime import datetime, UTC
from uuid import uuid4


@dataclass(frozen=True)
class RegisteredModel:
    id: str
    name: str
    created_at: datetime

    def create(cls, name: str) -> "RegisteredModel":
        return cls(
            id=uuid4(),
            name=name,
            created_at=datetime.now(UTC),
        )


@dataclass(frozen=True)
class ModelVersion:
    id: str
    model_id: str
    version: str
    artifact_id: str
    created_at: datetime

    def create(
        cls,
        model_id: str,
        version: int,
        artifact_id: str,
    ) -> "ModelVersion":
        return cls(
            id=uuid4(),
            model_id=model_id,
            version=version,
            artifact_id=artifact_id,
            created_at=datetime.now(UTC),
        )