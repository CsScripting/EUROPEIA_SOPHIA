from dataclasses import dataclass, field
from typing import Any, List, Optional

# Import DTOs
from ..module.dto import ModuleDTO
from ..week.dto import WeekDTO
from ..event_type.dto import EventTypeDTO
from ..academic_year.dto import AcademicYearDTO
from ..classroom.dto import ClassroomDTO
from ..student_group.dto import StudentGroupDTO
from ..teacher.dto import TeacherDTO
from ..typology.dto import TypologyDTO
from .dto import (
    EventApiDTO,
    ThirdPartyEventClientDTO,
    EventTicketEventDTO,
    DayOfWeekEnum
)

@dataclass
class Event:
    """
    Represents an Academic Event.

    This class encapsulates all data related to an event, including its scheduling,
    associated resources, and academic context. The fields of this class directly
    mirror the structure of EventApiDTO.

    Relationships:
    - eventType: EventTypeDTO (One-to-One) - The type of the event.
    - weeks: List[WeekDTO] (One-to-Many) - A list of weeks during which the event occurs.
    - classrooms: List[ClassroomDTO] (One-to-Many) - A list of classrooms where the event takes place.
    - module: Optional[ModuleDTO] (One-to-One, optional) - The academic module associated with the event.
    - academicYear: Optional[AcademicYearDTO] (One-to-One, optional) - The academic year of the event.
    - studentGroups: List[StudentGroupDTO] (One-to-Many) - A list of student groups attending the event.
    - thirdPartyEventClient: Optional[ThirdPartyEventClientDTO] (Placeholder) - Client for third-party events.
    - eventTicketEvent: Optional[EventTicketEventDTO] (Placeholder) - Ticketing information for the event.
    - usersEventRole: List[Any] (To be defined) - Roles of users associated with the event.
    - teachers: List[TeacherDTO] (One-to-Many) - Teachers involved in the event.
    - typologies: List[TypologyDTO] (To be defined) - Specific typologies of the event.
    - eventCompensationEvent: Optional[Any] (To be defined) - Information about event compensation.
    """
    # Mandatory fields
    # These rules should be enforced by validation logic elsewhere.
    startTime: str
    endTime: str
    duration: str
    day: DayOfWeekEnum
    eventType: EventTypeDTO
    numStudents: int
    wlsSectionName: str
    wlsSectionConnector: str
    annotations: str

    # Optional fields
    id: Optional[int] = None
    name: Optional[str] = None
    isOwner: Optional[bool] = None
    unit: Optional[str] = None
    weeks: List[WeekDTO] = field(default_factory=list)
    classrooms: List[ClassroomDTO] = field(default_factory=list)
    usersEventRole: List[Any] = field(default_factory=list)
    studentGroups: List[StudentGroupDTO] = field(default_factory=list)
    teachers: List[TeacherDTO] = field(default_factory=list)
    module: Optional[ModuleDTO] = None
    typologies: List[TypologyDTO] = field(default_factory=list)
    academicYear: Optional[AcademicYearDTO] = None
    thirdPartyEventClient: Optional[ThirdPartyEventClientDTO] = None
    eventCompensationEvent: Optional[Any] = None
    eventTicketEvent: Optional[EventTicketEventDTO] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dto(cls, dto: EventApiDTO) -> 'Event':
        """Creates an Event instance from an EventApiDTO."""
        return cls(
            # Mandatory fields
            startTime=dto.startTime,
            endTime=dto.endTime,
            duration=dto.duration,
            day=dto.day,
            eventType=dto.eventType,
            numStudents=dto.numStudents,
            wlsSectionName=dto.wlsSectionName,
            wlsSectionConnector=dto.wlsSectionConnector,
            annotations=dto.annotations,
            # Optional fields
            id=dto.id,
            name=dto.name,
            isOwner=dto.isOwner,
            unit=dto.unit,
            weeks=dto.weeks,
            classrooms=dto.classrooms,
            usersEventRole=list(dto.usersEventRole) if dto.usersEventRole is not None else [],
            studentGroups=dto.studentGroups,
            teachers=dto.teachers,
            module=dto.module,
            typologies=list(dto.typologies) if dto.typologies is not None else [],
            academicYear=dto.academicYear,
            thirdPartyEventClient=dto.thirdPartyEventClient,
            eventCompensationEvent=dto.eventCompensationEvent,
            eventTicketEvent=dto.eventTicketEvent,
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> EventApiDTO:
        """Returns the EventApiDTO representation of the Event."""
        return EventApiDTO(
            # Mandatory fields
            startTime=self.startTime,
            endTime=self.endTime,
            duration=self.duration,
            day=self.day,
            eventType=self.eventType,
            numStudents=self.numStudents,
            wlsSectionName=self.wlsSectionName,
            wlsSectionConnector=self.wlsSectionConnector,
            annotations=self.annotations,
            # Optional fields
            id=self.id,
            name=self.name,
            isOwner=self.isOwner,
            unit=self.unit,
            weeks=self.weeks,
            classrooms=self.classrooms,
            usersEventRole=list(self.usersEventRole),
            studentGroups=self.studentGroups,
            teachers=self.teachers,
            module=self.module,
            typologies=list(self.typologies),
            academicYear=self.academicYear,
            thirdPartyEventClient=self.thirdPartyEventClient,
            eventCompensationEvent=self.eventCompensationEvent,
            eventTicketEvent=self.eventTicketEvent,
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        )

    # You can add more methods here to manage Event-specific logic,
    # for example, methods to update certain fields, validate data, etc. 