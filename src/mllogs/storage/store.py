from abc import ABC, abstractmethod

from mllogs.run import Run


class Store(ABC):
    """
    DEPRECATED. Kept until the conversion to DB/File store split is made.
    """
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