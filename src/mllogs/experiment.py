from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime, UTC


@dataclass(frozen=True)
class Experiment:
    id: str
    name: str
    created_at: datetime

    @classmethod
    def create(cls, name: str) -> "Experiment":
        return cls(
            id=str(uuid4()),
            name=name,
            created_at=datetime.now(UTC),
        )