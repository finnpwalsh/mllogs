from dataclasses import dataclass


@dataclass(frozen=True)
class ArtifactRef:
    run_id: str
    name: str
    format: str