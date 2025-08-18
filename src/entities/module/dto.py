from dataclasses import dataclass
from typing import Any, Optional, Union

from ..scientific_area.dto import ScientificAreaDTO

@dataclass
class ModuleDTO:
    acronym: str
    code: str
    name: str
    degreeImportance: Any
    active: bool

    id: Optional[int] = None
    color: Optional[str] = None
    scientificArea: Optional[ScientificAreaDTO] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ModuleDTO':
        """Creates a ModuleDTO instance from a dictionary."""
        if not data:
            raise ValueError("Input data is None or empty, cannot create ModuleDTO with mandatory fields.")

        # Check for mandatory fields
        mandatory_fields = ['acronym', 'code', 'name', 'degreeImportance', 'active']
        for field_name in mandatory_fields:
            if field_name not in data:
                raise ValueError(f"Missing mandatory field '{field_name}' to create ModuleDTO from dict")

        # Handle nested ScientificAreaDTO
        scientific_area_data = data.get('scientificArea')
        scientific_area_dto: Optional[ScientificAreaDTO] = None
        if scientific_area_data is not None:
            if isinstance(scientific_area_data, dict):
                scientific_area_dto = ScientificAreaDTO.from_dict(scientific_area_data)
            else:
                # Or log a warning, or try to handle if it's an ID to be fetched, etc.
                # For now, strict dict expectation for nested DTOs.
                raise ValueError("Field 'scientificArea' is present but not a dictionary.")

        return cls(
            acronym=data['acronym'],
            code=data['code'],
            name=data['name'],
            degreeImportance=data['degreeImportance'], # Assuming direct pass-through for Any type
            active=data['active'],
            id=data.get('id'),
            color=data.get('color'),
            scientificArea=scientific_area_dto,
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt')
        )