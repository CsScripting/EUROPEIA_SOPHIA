from dataclasses import dataclass, field
from typing import Optional
from .dto import BuildingDTO
from ..campus.dto import CampusDTO

@dataclass
class Building:
    """
    Represents a Building entity.

    This class defines the structure for a building, including its name
    and its association with a campus.

    Relationships:
    - campus: Optional[CampusDTO] (One-to-One, optional) - The campus to which the building belongs.
    """
    # Mandatory fields
    name: str
    active: bool

    # Optional fields
    id: Optional[int] = None
    campus: Optional[CampusDTO] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dto(cls, dto: BuildingDTO) -> 'Building':
        return cls(
            id=dto.id,
            name=dto.name,
            campus=dto.campus, # Assuming CampusDTO is directly usable or add conversion
            active=dto.active,
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> BuildingDTO:
        return BuildingDTO(
            id=self.id,
            name=self.name,
            campus=self.campus, # Assuming CampusDTO is directly usable or add conversion
            active=self.active,
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        ) 