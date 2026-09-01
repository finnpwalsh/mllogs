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


class RunStatus(Enum):
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class Artifact:
    name: str
    uri: str
    artifact_type: str