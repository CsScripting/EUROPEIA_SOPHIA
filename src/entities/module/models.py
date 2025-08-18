from dataclasses import dataclass
from typing import Any, Optional

from .dto import ModuleDTO
from ..scientific_area.dto import ScientificAreaDTO

@dataclass
class Module:
    """
    Represents a Module entity.

    This class defines an academic module, which can be part of a larger
    scientific area. It includes details such as acronym, code, and name.

    Relationships:
    - scientificArea: Optional[ScientificAreaDTO] (One-to-One, optional) - The scientific area of the module.
    """
    # Mandatory fields
    acronym: str
    code: str
    name: str
    degreeImportance: Any
    active: bool

    # Optional fields
    id: Optional[int] = None
    color: Optional[str] = None
    scientificArea: Optional[ScientificAreaDTO] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dto(cls, dto: ModuleDTO) -> 'Module':
        """Creates a Module instance from a ModuleDTO."""
        return cls(
            acronym=dto.acronym,
            code=dto.code,
            name=dto.name,
            degreeImportance=dto.degreeImportance,
            active=dto.active,
            id=dto.id,
            color=dto.color,
            scientificArea=dto.scientificArea,
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> ModuleDTO:
        """Returns the ModuleDTO representation of the Module."""
        return ModuleDTO(
            acronym=self.acronym,
            code=self.code,
            name=self.name,
            degreeImportance=self.degreeImportance,
            active=self.active,
            id=self.id,
            color=self.color,
            scientificArea=self.scientificArea,
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        ) 