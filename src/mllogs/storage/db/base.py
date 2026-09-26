from abc import ABC, abstractmethod

from mllogs.run import Run
from mllogs.types import ParamValue
from mllogs.artifact import ArtifactRef


class DBStore(ABC):
    # ================
    # ----- RUNS -----
    # ================

    @abstractmethod
    def save_run(self, run: Run) -> None: ...

    @abstractmethod
    def update_run(self, run: Run) -> None: ...

    @abstractmethod
    def load_run(self, run_id: str) -> Run: ...

    @abstractmethod
    def delete_run(self, run_id: str) -> None: ...


    # ========================
    # ----- RUN METADATA -----
    # ========================

    @abstractmethod
    def save_param(self, run_id: str, key: str, value: ParamValue) -> None: ...

    @abstractmethod
    def load_params(self, run_id: str) -> dict[str, ParamValue]: ...
    
    @abstractmethod
    def save_metric(self, run_id: str, key: str, value: float) -> None: ...
    
    @abstractmethod
    def load_metrics(self, run_id: str) -> dict[str, float]: ...
    
    @abstractmethod
    def save_tag( self, run_id: str, key: str, value: str) -> None: ...

    @abstractmethod
    def load_tags(self, run_id: str) -> dict[str, str]: ...


    # =====================
    # ----- ARTIFACTS -----
    # =====================

    @abstractmethod
    def save_artifact_ref(self, ref: ArtifactRef) -> None: ...

    @abstractmethod
    def load_artifact_refs(self, run_id: str) -> list[ArtifactRef]: ...