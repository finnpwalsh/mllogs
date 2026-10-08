from abc import ABC, abstractmethod

from mllogs.experiment import Experiment
from mllogs.run import Run
from mllogs.types import ParamValue
from mllogs.artifact import ArtifactRef
from mllogs.model.models import RegisteredModel, ModelVersion


class DBStore(ABC):
    # =======================
    # ----- EXPERIMENTS -----
    # =======================

    @abstractmethod
    def save_experiment(self, experiment: Experiment) -> None: ...

    @abstractmethod
    def load_experiment(self, experiment_id: str) -> Experiment: ...

    @abstractmethod
    def load_experiment_by_name(self, name: str) -> Experiment: ...

    @abstractmethod
    def load_experiments(self) -> list[Experiment]: ...

    @abstractmethod
    def delete_experiment(self, experiment_id: str) -> None: ...

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
    def load_runs(self, experiment_id: str | None = None) -> list[Run]: ...

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
    def load_artifact_ref(self, artifact_id: str) -> ArtifactRef: ...

    @abstractmethod
    def load_artifact_refs(self, run_id: str) -> list[ArtifactRef]: ...

    @abstractmethod
    def load_artifact_ref_by_name(self, run_id: str, name: str) -> ArtifactRef: ...


    # ==================
    # ----- MODELS -----
    # ==================

    @abstractmethod
    def save_registered_model(self, model: RegisteredModel) -> None: ...

    @abstractmethod
    def load_registered_model(self, model_id: str) -> RegisteredModel: ...

    @abstractmethod
    def load_registered_model_by_name(self, name: str) -> RegisteredModel: ...

    @abstractmethod
    def save_model_version(self, model_version: ModelVersion) -> None: ...

    @abstractmethod
    def load_model_version(self, model_version_id: str) -> ModelVersion: ...

    @abstractmethod
    def load_model_version_by_model(self, model_id: str, version: int) -> ModelVersion: ...

    @abstractmethod
    def load_model_versions(self, model_id: str) -> list[ModelVersion]: ...

    @abstractmethod
    def load_latest_model_version(self, model_id: str) -> ModelVersion: ...