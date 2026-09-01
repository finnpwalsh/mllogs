from pathlib import Path

from .run import Run


class LocalFileStore:
    def __init__(self, root_dir: str | Path = ".mllogs") -> None:
        self._root_dir = root_dir
        self._runs_dir = self._root_dir / "runs"

        self._runs_dir.mkdir(parents=True, exist_ok=True)

    
    def save_run(self, run: Run) -> None:
        ...

    def load_run(self, run_id: str) -> Run:
        ...

    def list_runs(self, limit: int = 10) -> list[Run]:
        ...

    def delete_run(self, run_id: str) -> None:
        ...