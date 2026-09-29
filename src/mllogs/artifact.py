from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class ArtifactRef:
    id: str
    run_id: str
    name: str
    format: str

    @classmethod
    def create(
        cls,
        run_id: str,
        name: str,
        format: str,
    ) -> "ArtifactRef":
        return cls(
            id=str(uuid4()),
            run_id=run_id,
            name=name,
            format=format,
        )

    @property
    def uri(self) -> str:
        return f"{self.run_id}/{self.name}.{self.format}"