from dataclasses import dataclass
from datetime import datetime, UTC
from uuid import uuid4


@dataclass(frozen=True)
class RegisteredModel:
    id: str
    name: str
    created_at: datetime

    @classmethod
    def create(cls, name: str) -> "RegisteredModel":
        return cls(
            id=str(uuid4()),
            name=name,
            created_at=datetime.now(UTC),
        )


@dataclass(frozen=True)
class ModelVersion:
    id: str
    model_id: str
    version: int
    artifact_id: str
    created_at: datetime

    @classmethod
    def create(
        cls,
        model_id: str,
        version: int,
        artifact_id: str,
    ) -> "ModelVersion":
        return cls(
            id=str(uuid4()),
            model_id=model_id,
            version=version,
            artifact_id=artifact_id,
            created_at=datetime.now(UTC),
        )


@dataclass
class ModelAlias:
    id: str
    model_id: str
    name: str
    version_id: str

    @classmethod
    def create(
        cls,
        model_id: str,
        name: str,
        version_id: str,
    ) -> "ModelAlias":
        return cls(
            id=str(uuid4()),
            model_id=model_id,
            name=name,
            version_id=version_id,
        )