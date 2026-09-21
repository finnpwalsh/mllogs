from abc import ABC, abstractmethod

from mllogs.run import Run
from mllogs.types import ParamValue


class DBStore(ABC):
    # =================
    # ----- Write -----
    # =================

    # --- Runs ----

    @abstractmethod
    def save_run(self, run: Run) -> None:
        ...

    @abstractmethod
    def update_run(self, run: Run) -> None:
        ...

    @abstractmethod
    def delete_run(self, run_id: str) -> None:
        ...

    # --- Params ---

    @abstractmethod
    def save_param(
        self,
        run_id: str,
        key: str,
        value: ParamValue,
    ) -> None:
        ...

    # --- Metrics ---

    @abstractmethod
    def save_metric(
        self,
        run_id: str,
        key: str,
        value: float,
    ) -> None:
        ...

    # --- Tags ---

    @abstractmethod
    def save_tag(
        self,
        run_id: str,
        key: str,
        value: str,
    ) -> None:
        ...

    # ================
    # ----- Read -----
    # ================

    @abstractmethod
    def load_run(self, run_id: str) -> Run:
        ...

    @abstractmethod
    def load_params(self, run_id: str) -> dict[str, ParamValue]:
        ...

    @abstractmethod
    def load_metrics(self, run_id: str) -> dict[str, float]:
        ...

    @abstractmethod
    def load_tags(self, run_id: str) -> dict[str, str]:
        ...


    # ==================
    # ----- Delete -----
    # ==================

    @abstractmethod
    def delete_run(self, run_id: str) -> None:
        ...