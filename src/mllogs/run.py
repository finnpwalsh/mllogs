from datetime import datetime
from dataclasses import dataclass
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

    params: dict[str, Any]
    metrics: dict[str, float]
    tags: dict[str, str]


class RunType(Enum):
    TRAIN = "train"
    EVAL = "eval"
    INFERENCE = "inference"


class RunStatus(Enum):
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"