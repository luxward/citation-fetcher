import dataclasses


@dataclasses.dataclass
class Paper:
    title: str
    cite: str
    id: str
    doi: str = ""
