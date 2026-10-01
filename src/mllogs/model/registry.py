from mllogs.storage.db import DBStore
from .models import RegisteredModel, ModelVersion
from mllogs.artifact import ArtifactRef


class ModelRegistry:
    def __init__(self, db_store: DBStore):
        self._db_store = db_store
    
    
    # ===================
    # ----- HELPERS -----
    # ===================

    def _get_registered_model(self, name: str) -> RegisteredModel:
        return self._db_store.load_registered_model_by_name(name)

    def _get_or_create_registered_model(self, name: str) -> RegisteredModel:
        try:
            return self._get_registered_model(name)
        except KeyError:
            return self.register_model(name)


    # ====================
    # ----- REGISTRY -----
    # ====================

    # --- Registered Model ---
    def register_model(self, name: str) -> RegisteredModel:
        model = RegisteredModel.create(name)
        self._db_store.save_registered_model(model)
        return model

    # --- Model Version ---
    def create_version(self, model_name: str, artifact_ref: ArtifactRef) -> ModelVersion:
        registered_model = self._get_or_create_registered_model(model_name)

        try:
            latest = self._db_store.load_latest_model_version(registered_model.id)
            version = latest.version + 1
        except KeyError:
            version = 1

        model_version = ModelVersion.create(
            model_id=registered_model.id,
            version=version,
            artifact_id=artifact_ref.id,
        )

        self._db_store.save_model_version(model_version)
        return model_version

    def get_version(self, model_name: str, version: int) -> ModelVersion:
        model = self._get_registered_model(model_name)

        return self._db_store.load_model_version_by_model(
            model_id=model.id,
            version=version,
        )

    def get_latest_version(self, model_name: str) -> ModelVersion:
        model = self._get_registered_model(model_name)
        return self._db_store.load_latest_model_version(model.id)