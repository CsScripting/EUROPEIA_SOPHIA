from dataclasses import dataclass
from typing import Optional
from .dto import LabourContractDTO

@dataclass
class LabourContract:
    """
    Represents a Labour Contract entity.

    This class defines the type of labour contract associated with personnel,
    such as teachers.
    """
    # Mandatory fields
    active: bool

    # Optional fields
    id: Optional[int] = None
    name: Optional[str] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dto(cls, dto: LabourContractDTO) -> 'LabourContract':
        return cls(
            id=dto.id,
            name=dto.name,
            active=dto.active,
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> LabourContractDTO:
        return LabourContractDTO(
            id=self.id,
            name=self.name,
            active=self.active,
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        ) 