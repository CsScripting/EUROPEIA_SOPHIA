from dataclasses import dataclass
from typing import Optional

@dataclass
class FloorDTO:
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
    def from_dict(cls, data: dict) -> 'FloorDTO':
        """Creates a FloorDTO instance from a dictionary."""
        if not data:
            raise ValueError("Input data is None or empty, cannot create FloorDTO with mandatory fields.")

        # Check for mandatory fields
        if 'name' not in data or 'active' not in data:
            raise ValueError("Missing one or more mandatory fields (name, active) to create FloorDTO from dict")

        return cls(
            name=data['name'],
            active=data['active'],
            id=data.get('id'),
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt')
        ) 