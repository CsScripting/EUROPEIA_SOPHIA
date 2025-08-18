from dataclasses import dataclass
from typing import Optional
from .dto import FloorDTO

@dataclass
class Floor:
    """
    Represents a Floor entity.

    This class defines a floor level (e.g., '1st Floor', 'Ground Floor')
    that can be associated with a Classroom as its location.
    """
    # Mandatory fields
    name: str
    active: bool

    # Optional fields
    id: Optional[int] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dto(cls, dto: FloorDTO) -> 'Floor':
        return cls(
            id=dto.id,
            name=dto.name,
            active=dto.active,
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> FloorDTO:
        return FloorDTO(
            id=self.id,
            name=self.name,
            active=self.active,
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        ) 