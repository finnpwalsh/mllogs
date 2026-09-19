from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from .artifact import Artifact


class RunStatus(Enum):
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class Run:
    id: str
    started_at: datetime
    status: RunStatus

    name: str | None = None
    run_type: str | None =  None
    ended_at: datetime | None = None

    params: dict[str, str | int | float | bool] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
    artifacts: list[Artifact] = field(default_factory=list)