from datetime import datetime
from dataclasses import dataclass, field
from typing import Any
from enum import Enum


class RunStatus(Enum):
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class Artifact:
    name: str
    uri: str
    artifact_type: str

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "uri": self.uri,
            "artifact_type": self.artifact_type,
        }


    @classmethod
    def from_dict(cls, d: dict[str, str]) -> "Artifact":
        return cls(
            name = d["name"],
            uri = d["uri"],
            artifact_type = d["artifact_type"],
        )


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
    artifacts: list[Artifact] = field(default_factory=list)


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
            "artifacts": [a.to_dict() for a in self.artifacts],
        }


    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Run":
        return cls(
            id = d["id"],
            started_at = datetime.fromisoformat(d["started_at"]),
            status = RunStatus(d["status"]),
            name = d["name"],
            run_type = d["run_type"],
            ended_at = (
                datetime.fromisoformat(d["ended_at"])
                if d["ended_at"] is not None
                else None
            ),
            params = d["params"],
            metrics = d["metrics"],
            tags = d["tags"],
            artifacts = [Artifact.from_dict(a) for a in d["artifacts"]],
        )