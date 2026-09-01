from datetime import datetime
from dataclasses import dataclass, field
from typing import Any
from enum import Enum


@dataclass
class Run:
    id: str
    started_at: datetime
    status: RunStatus

    name: str | None = None
    run_type: str | None =  None
    ended_at: datetime | None = None

    params: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)

    artifacts: list[Artifact] | None = None


    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "started_at": self.started_at.isoformat(),
            "status": self.status.value,
            "name": self.name,
            "run_type": self.run_type,
            "ended_at": (
                self.ended_at.isoformat()
                if self.ended_at is not None
                else None
            ),
            "params": self.params,
            "metrics": self.metrics,
            "tags": self.tags,
            "artifacts": self.artifacts,
        }


class RunStatus(Enum):
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class Artifact:
    name: str
    uri: str
    artifact_type: str