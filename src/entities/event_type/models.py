from dataclasses import dataclass, field
from typing import Any, Optional, List

from .dto import EventTypeDTO

@dataclass
class EventType:
    """
    Represents an Event Type entity.

    This class defines the type of an event, including its name and color code.
    It helps categorize different kinds of events.
    """
    # Mandatory fields
    name: str
    color: str
    active: bool

    # Optional fields
    id: Optional[int] = None
    setToAplication: Optional[bool] = None
    resourceMetadataEntries: List[Any] = field(default_factory=list)
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dto(cls, dto: EventTypeDTO) -> 'EventType':
        """Creates an EventType instance from an EventTypeDTO."""
        return cls(
            name=dto.name,
            color=dto.color,
            active=dto.active,
            id=dto.id,
            setToAplication=dto.setToAplication,
            resourceMetadataEntries=list(dto.resourceMetadataEntries) if dto.resourceMetadataEntries is not None else [],
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> EventTypeDTO:
        """Returns the EventTypeDTO representation of the EventType."""
        return EventTypeDTO(
            name=self.name,
            color=self.color,
            active=self.active,
            id=self.id,
            setToAplication=self.setToAplication,
            resourceMetadataEntries=list(self.resourceMetadataEntries),
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        ) 