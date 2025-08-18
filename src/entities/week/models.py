from dataclasses import dataclass
from typing import Any, Optional

from .dto import WeekDTO

@dataclass
class Week:
    """
    Represents a Week entity.

    This class defines a specific week, typically by its start date,
    and is used in the context of event scheduling.
    """
    # Mandatory fields
    startDate: str

    # Optional fields
    id: Optional[int] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dto(cls, dto: WeekDTO) -> 'Week':
        """Creates a Week instance from a WeekDTO."""
        return cls(
            startDate=dto.startDate,
            id=dto.id,
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> WeekDTO:
        """Returns the WeekDTO representation of the Week."""
        return WeekDTO(
            startDate=self.startDate,
            id=self.id,
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        ) 