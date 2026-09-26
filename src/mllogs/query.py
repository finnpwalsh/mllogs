from typing import Any

from .artifact import ArtifactRef
from .run import Run
from .serializers import get_serializer
from .storage.db import DBStore
from .storage.artifacts import ArtifactStore
from .types import ParamValue


class Query:
    # ======================
    # ----- INITIALIZE -----
    # ======================
    
    def __init__(
        self,
        db_store: DBStore,
        artifact_store: ArtifactStore,
    ) -> None:
        self._db_store = db_store
        self._artifact_store = artifact_store


    # ===============
    # ----- RUN -----
    # ===============

    def get_run(self, run_id: str) -> Run:
        return self._db_store.load_run(run_id)


    # ========================
    # ----- RUN METADATA -----
    # ========================

    def get_params(self, run_id: str) -> dict[str, ParamValue]:
        return self._db_store.load_params(run_id)

    def get_metrics(self, run_id: str) -> dict[str, float]:
        return self._db_store.load_metrics(run_id)

    def get_tags(self, run_id: str) -> dict[str, str]:
        return self._db_store.load_tags(run_id)


    # ====================
    # ----- ARTIFACT -----
    # ====================

    def list_artifacts(self, run_id: str) -> list[str]:
        artifact_refs = self._db_store.load_artifact_refs(run_id)
        return [ref.name for ref in artifact_refs]


    def load_artifact(
        self,
        run_id: str,
        name: str,
    ) -> Any:
        artifact_refs = self._db_store.load_artifact_refs(run_id)
        
        artifact_ref = None
        for ref in artifact_refs:
            if ref.name == name:
                artifact_ref = ref
                break

        if artifact_ref is None:
            raise KeyError(f"Artifact '{name}' not found for run '{run_id}'.")

        serializer = get_serializer(artifact_ref.format)
        data = self._artifact_store.load(artifact_ref.uri)
        return serializer.deserialize(data)