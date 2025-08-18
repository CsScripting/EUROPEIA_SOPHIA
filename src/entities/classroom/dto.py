from dataclasses import dataclass, field
from typing import Any, Optional, List
from ..building.dto import BuildingDTO
from ..floor.dto import FloorDTO
from ..characteristic.dto import CharacteristicDTO

@dataclass
class ClassroomDTO:
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
    def from_dict(cls, data: dict) -> 'ClassroomDTO':
        """Creates a ClassroomDTO instance from a dictionary."""
        if not data:
            raise ValueError("Input data is None or empty, cannot create ClassroomDTO with mandatory fields.")

        # Check for mandatory fields (excluding those with default_factory if not present in API dict)
        mandatory_fields = ['name', 'code', 'capacity', 'capacityExam', 'capacityMargin', 'email', 'building', 'active']
        for field_name in mandatory_fields:
            if field_name not in data:
                raise ValueError(f"Missing mandatory field '{field_name}' to create ClassroomDTO from dict")

        # Handle nested BuildingDTO (mandatory)
        building_data = data['building'] # Already checked for presence
        if not isinstance(building_data, dict):
            raise ValueError("Field 'building' must be a dictionary.")
        building_dto = BuildingDTO.from_dict(building_data)

        # Handle nested FloorDTO (optional)
        floor_data = data.get('floor')
        floor_dto: Optional[FloorDTO] = None
        if floor_data is not None:
            if isinstance(floor_data, dict):
                floor_dto = FloorDTO.from_dict(floor_data)
            else:
                raise ValueError("Field 'floor' is present but not a dictionary.")

        # Handle list of CharacteristicDTOs
        characteristics_list_data = data.get('characteristics', [])
        characteristics_dto_list: List[CharacteristicDTO] = []
        if not isinstance(characteristics_list_data, list):
            # Or log warning and use empty list if API might send non-list for empty
            raise ValueError("Field 'characteristics' must be a list.") 
        for char_data in characteristics_list_data:
            if isinstance(char_data, dict):
                characteristics_dto_list.append(CharacteristicDTO.from_dict(char_data))
            else:
                # Or skip this item, or log warning
                raise ValueError("Item in 'characteristics' list is not a dictionary.")

        return cls(
            name=data['name'],
            code=data['code'],
            capacity=data['capacity'],
            capacityExam=data['capacityExam'],
            capacityMargin=data['capacityMargin'],
            email=data['email'],
            building=building_dto,
            active=data['active'],
            characteristics=characteristics_dto_list,
            id=data.get('id'),
            observations=data.get('observations'),
            belongsToMyGroups=data.get('belongsToMyGroups'),
            canCreateAnEvent=data.get('canCreateAnEvent'),
            canRequestAnEvent=data.get('canRequestAnEvent'),
            isMyFavorite=data.get('isMyFavorite'),
            classroomGroups=data.get('classroomGroups', []),
            classroomGroupsBookings=data.get('classroomGroupsBookings', []),
            floor=floor_dto,
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt')
        )