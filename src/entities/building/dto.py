from dataclasses import dataclass, field
from typing import Optional, Any
from ..campus.dto import CampusDTO

# Placeholder DTO - Define this properly if it becomes a full entity

@dataclass
class BuildingDTO:
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
    def from_dict(cls, data: dict) -> 'BuildingDTO':
        """Creates a BuildingDTO instance from a dictionary."""
        if not data:
            raise ValueError("Input data is None or empty, cannot create BuildingDTO with mandatory fields.")

        # Check for mandatory fields
        if 'name' not in data or 'active' not in data:
            raise ValueError("Missing one or more mandatory fields (name, active) to create BuildingDTO from dict")

        # Handle nested CampusDTO
        campus_data = data.get('campus')
        campus_dto: Optional[CampusDTO] = None
        if campus_data is not None:
            if isinstance(campus_data, dict):
                campus_dto = CampusDTO.from_dict(campus_data)
            else:
                raise ValueError("Field 'campus' is present but not a dictionary.")

        return cls(
            name=data['name'],
            active=data['active'],
            id=data.get('id'),
            campus=campus_dto,
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt')
        ) 