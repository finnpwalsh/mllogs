from datetime import datetime
from dataclasses import dataclass, field
from typing import Any
from enum import Enum


@dataclass
class Run:
    id: str
    name: str

    run_type: RunType
    status: RunStatus

    started_at: datetime
    ended_at: datetime | None = None

    params: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)

    artifacts: list[Artifact] | None = None


class RunType(Enum):
    TRAIN = "train"
    EVAL = "eval"
    INFERENCE = "inference"


class RunStatus(Enum):
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class Artifact:
    name: str
    uri: str
    artifact_type: str