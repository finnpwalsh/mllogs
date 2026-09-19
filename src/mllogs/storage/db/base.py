from abc import ABC, abstractmethod

from mllogs.run import Run
from mllogs.artifact import Artifact


class DBStore(ABC):
    @abstractmethod
    def save_run(self, run: Run) -> None:
        ...

    @abstractmethod
    def load_run(self, run_id: str | None = None) -> Run | None:
        ...

    @abstractmethod
    def list_runs(self, limit: int | None = None) -> list[Run]:
        ...

    @abstractmethod
    def delete_run(self, run_id: str) -> None:
        ...

    @abstractmethod
    def save_artifact(
        self,
        run_id: str,
        artifact: Artifact,
    ) -> None:
        ...

    @abstractmethod
    def delete_artifact(
        self,
        run_id: str,
        artifact: Artifact,
    ) -> None:
        ...