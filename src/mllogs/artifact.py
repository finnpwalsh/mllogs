from dataclasses import dataclass


@dataclass(frozen=True)
class ArtifactRef:
    run_id: str
    name: str
    format: str

    @property
    def uri(self) -> str:
        return f"{self.run_id}/{self.name}.{self.format}"