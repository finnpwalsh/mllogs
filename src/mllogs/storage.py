from pathlib import Path
import json

from .run import Run


class LocalFileStore:
    def __init__(self, root_dir: str | Path = ".mllogs") -> None:
        """
        Initializes LocalFileStore and creates runs directory if it
        does not already exist.
        """
        self._root_dir = Path(root_dir)
        self._runs_dir = self._root_dir / "runs"

        self._runs_dir.mkdir(parents=True, exist_ok=True)

    def save_run(self, run: Run) -> None:
        """
        Writes Run to storage as JSON file.
        """
        path = self._runs_dir / f"{run.id}.json"

        with path.open("w") as f:
            json.dump(run.to_dict(), f, indent=4)


    def load_run(self, run_id: str) -> Run:
        """
        Reads JSON run file from storage and returns a Run.
        """
        path = self._runs_dir / f"{run_id}.json"

        with path.open("r") as f:
            run_dict = json.load(f)

        return Run.from_dict(run_dict)

    
    def list_runs(self, limit: int | None = None) -> list[Run]:
        """
        Returns the most recent runs.

        If limit is None, returns all runs.
        """
        if limit is not None and limit <= 0:
            raise ValueError("limit must be greater than 0")

        paths = sorted(
            self._runs_dir.glob("*.json"),
            reverse=True, # latest first
        )

        if limit is not None:
            paths = paths[:limit]

        runs = []

        for path in paths:
            run = self.load_run(path.stem)
            runs.append(run)

        return runs


    def delete_run(self, run_id: str) -> None:
        """
        Deletes a run from storage by run ID.
        """
        path = self._runs_dir / f"{run_id}.json"

        path.unlink()