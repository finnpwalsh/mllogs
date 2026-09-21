from datetime import datetime, UTC
from uuid import uuid4
from dataclasses import dataclass, field
from enum import Enum


class RunStatus(Enum):
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class Run:
    id: str
    started_at: datetime
    status: RunStatus
    ended_at: datetime | None = None

    @classmethod
    def create(cls) -> "Run":
        started_at = datetime.now(UTC)

        timestamp = started_at.strftime("%Y%m%d%H%M%S")
        run_id = f"{timestamp}-{uuid4().hex[:8]}"

        return cls(
            id=run_id,
            started_at=started_at,
            status=RunStatus.RUNNING,
        )