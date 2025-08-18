from dataclasses import dataclass
from typing import Any, Optional

from .dto import AcademicYearDTO

@dataclass
class AcademicYear:
    """
    Represents an Academic Year entity.

    This class defines an academic year, typically with a name, start date,
    and end date, used for contextualizing events and academic activities.
    """
    # Mandatory fields
    active: bool

    # Optional fields
    id: Optional[int] = None
    name: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dto(cls, dto: AcademicYearDTO) -> 'AcademicYear':
        """Creates an AcademicYear instance from an AcademicYearDTO."""
        return cls(
            active=dto.active,
            id=dto.id,
            name=dto.name,
            startDate=dto.startDate,
            endDate=dto.endDate,
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> AcademicYearDTO:
        """Returns the AcademicYearDTO representation of the AcademicYear."""
        return AcademicYearDTO(
            active=self.active,
            id=self.id,
            name=self.name,
            startDate=self.startDate,
            endDate=self.endDate,
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        ) 