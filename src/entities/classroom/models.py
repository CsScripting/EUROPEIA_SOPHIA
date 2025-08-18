from dataclasses import dataclass, field
from typing import Any, Optional, List

from .dto import ClassroomDTO
from ..building.dto import BuildingDTO
from ..floor.dto import FloorDTO
from ..characteristic.dto import CharacteristicDTO

@dataclass
class Classroom:
    """
    Represents a Classroom entity.

    This class defines the structure for a classroom, including its physical attributes,
    location (building and floor), and associated characteristics.

    Relationships:
    - building: BuildingDTO (One-to-One) - The building where the classroom is located.
    - characteristics: List[CharacteristicDTO] (One-to-Many) - A list of characteristics of the classroom.
    - floor: Optional[FloorDTO] (One-to-One, optional) - The floor where the classroom is located.
    - classroomGroups: List[Any] (To be defined) - Groups associated with the classroom.
    - classroomGroupsBookings: List[Any] (To be defined) - Bookings for classroom groups.
    """
    # Mandatory fields
    name: str
    code: str
    capacity: int
    capacityExam: int
    capacityMargin: int
    email: str
    building: BuildingDTO
    active: bool
    characteristics: List[CharacteristicDTO] = field(default_factory=list)

    # Optional fields
    id: Optional[int] = None
    observations: Optional[str] = None
    belongsToMyGroups: Optional[bool] = None
    canCreateAnEvent: Optional[bool] = None
    canRequestAnEvent: Optional[bool] = None
    isMyFavorite: Optional[bool] = None
    classroomGroups: List[Any] = field(default_factory=list)
    classroomGroupsBookings: List[Any] = field(default_factory=list)
    floor: Optional[FloorDTO] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dto(cls, dto: ClassroomDTO) -> 'Classroom':
        """Creates a Classroom instance from a ClassroomDTO."""
        return cls(
            name=dto.name,
            code=dto.code,
            capacity=dto.capacity,
            capacityExam=dto.capacityExam,
            capacityMargin=dto.capacityMargin,
            email=dto.email,
            building=dto.building,
            active=dto.active,
            characteristics=dto.characteristics,
            id=dto.id,
            observations=dto.observations,
            belongsToMyGroups=dto.belongsToMyGroups,
            canCreateAnEvent=dto.canCreateAnEvent,
            canRequestAnEvent=dto.canRequestAnEvent,
            isMyFavorite=dto.isMyFavorite,
            classroomGroups=dto.classroomGroups,
            classroomGroupsBookings=dto.classroomGroupsBookings,
            floor=dto.floor,
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> ClassroomDTO:
        """Returns the ClassroomDTO representation of the Classroom."""
        return ClassroomDTO(
            name=self.name,
            code=self.code,
            capacity=self.capacity,
            capacityExam=self.capacityExam,
            capacityMargin=self.capacityMargin,
            email=self.email,
            building=self.building,
            active=self.active,
            characteristics=self.characteristics,
            id=self.id,
            observations=self.observations,
            belongsToMyGroups=self.belongsToMyGroups,
            canCreateAnEvent=self.canCreateAnEvent,
            canRequestAnEvent=self.canRequestAnEvent,
            isMyFavorite=self.isMyFavorite,
            classroomGroups=self.classroomGroups,
            classroomGroupsBookings=self.classroomGroupsBookings,
            floor=self.floor,
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        ) 