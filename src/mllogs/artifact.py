from dataclasses import dataclass


@dataclass
class Artifact:
    """
    Represents an artifact produced by an experiment run.

    Attributes:
        name: Name of the artifact, e.g. "baseline_model"
        artifact_type: Type of artifact, e.g. "model"
        format: Serialization format, e.g. "pickle"
    """
    
    name: str
    artifact_type: str
    format: str

    @property
    def filename(self) -> str:
        return f"{self.name}.{self.format}"