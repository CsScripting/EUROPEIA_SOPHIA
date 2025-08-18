from dataclasses import dataclass
from typing import Any, Optional

from .dto import ScientificAreaDTO

@dataclass
class ScientificArea:
    """
    Represents a Scientific Area entity.

    This class defines a scientific area, which can be associated with academic modules.
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
    def from_dto(cls, dto: ScientificAreaDTO) -> 'ScientificArea':
        """Creates a ScientificArea instance from a ScientificAreaDTO."""
        return cls(
            name=dto.name,
            active=dto.active,
            id=dto.id,
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> ScientificAreaDTO:
        """Returns the ScientificAreaDTO representation of the ScientificArea."""
        return ScientificAreaDTO(
            name=self.name,
            active=self.active,
            id=self.id,
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        ) 