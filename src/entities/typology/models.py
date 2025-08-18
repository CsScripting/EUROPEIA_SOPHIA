from dataclasses import dataclass
from typing import Optional

from .dto import TypologyDTO

@dataclass
class Typology:
    name: str
    color: str
    constAvoidPeriodTypology: str
    active: bool
    id: Optional[int] = None
    description: Optional[str] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dto(cls, dto: TypologyDTO) -> "Typology":
        return cls(
            id=dto.id,
            name=dto.name,
            description=dto.description,
            color=dto.color,
            constAvoidPeriodTypology=dto.constAvoidPeriodTypology,
            active=dto.active,
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> TypologyDTO:
        return TypologyDTO(
            id=self.id,
            name=self.name,
            description=self.description,
            color=self.color,
            constAvoidPeriodTypology=self.constAvoidPeriodTypology,
            active=self.active,
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        ) 