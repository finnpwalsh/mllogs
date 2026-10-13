from typing import Any

from mllogs.storage.db import DBStore
from mllogs.storage.artifacts import ArtifactStore
from .models import RegisteredModel, ModelVersion, ModelAlias
from mllogs.serializers import get_serializer
from mllogs.artifact import ArtifactRef


class ModelRegistry:
    def __init__(
        self,
        db_store: DBStore,
        artifact_store: ArtifactStore,
    ) -> None:
        self._db_store = db_store
        self._artifact_store = artifact_store
    
    
    # ===================
    # ----- HELPERS -----
    # ===================

    def _get_registered_model(self, name: str) -> RegisteredModel:
        return self._db_store.load_registered_model_by_name(name)


    # ====================
    # ----- REGISTRY -----
    # ====================

    # --- Registered Model ---

    def register_model(self, name: str) -> RegisteredModel:
        try:
            return self._get_registered_model(name)
        except KeyError:
            model = RegisteredModel.create(name)
            self._db_store.save_registered_model(model)
            return model


    # --- Model Version ---

    def create_version(self, model_name: str, artifact_ref: ArtifactRef) -> ModelVersion:
        registered_model = self.register_model(model_name)

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

    # --- Model Alias ---

    def set_alias(self, model_version: ModelVersion, alias_name: str) -> ModelAlias:
        model = self._db_store.load_registered_model(model_version.model_id)

        try:
            alias = self.get_alias(model.name, alias_name)
            alias.version_id = model_version.id
        except KeyError:
            alias = ModelAlias.create(
                model_version.model_id,
                name=alias_name,
                version_id=model_version.id,
            )

        self._db_store.save_model_alias(alias)

        return alias

    def get_alias(self, model_name: str, alias_name: str) -> ModelAlias:
        return self._db_store.load_model_alias_by_name(model_name=model_name, alias_name=alias_name)

    def get_version_by_alias(self, model_name: str, alias_name: str) -> ModelVersion:
        alias = self.get_alias(model_name, alias_name)

        return self._db_store.load_model_version(alias.version_id)

    def load_model(
        self,
        model_name: str,
        *,
        version: int | None = None,
        alias: str | None = None,
    ) -> Any:
        if version is not None and alias is not None:
            raise ValueError("Specify either 'version' or 'alias', not both.")
        
        # check model is registered
        model = self._db_store.load_registered_model_by_name(model_name)

        if version is not None:
            model_version = self._db_store.load_model_version_by_model(model.id, version)

        elif alias is not None:
            version_id = self._db_store.load_model_alias_by_name(model_name, alias).version_id
            model_version = self._db_store.load_model_version(version_id)

        else:
            model_version = self._db_store.load_latest_model_version(model.id)

        artifact_ref = self._db_store.load_artifact_ref(model_version.artifact_id)
        
        data = self._artifact_store.load(artifact_ref.uri)
        serializer = get_serializer(artifact_ref.format)

        return serializer.deserialize(data)