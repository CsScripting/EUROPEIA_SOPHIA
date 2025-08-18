from dataclasses import dataclass
from typing import Optional

@dataclass
class CampusDTO:
    # Mandatory fields
    name: str
    active: bool

    # Optional fields
    id: Optional[int] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None # Consider datetime object or ISO string
    createdAt: Optional[str] = None      # Consider datetime object or ISO string 

    @classmethod
    def from_dict(cls, data: dict) -> 'CampusDTO':
        """Creates a CampusDTO instance from a dictionary."""
        if not data:
            raise ValueError("Input data is None or empty, cannot create CampusDTO with mandatory fields.")

        # Check for mandatory fields
        if 'name' not in data or 'active' not in data:
            raise ValueError("Missing one or more mandatory fields (name, active) to create CampusDTO from dict")

        return cls(
            name=data['name'],
            active=data['active'],
            id=data.get('id'),
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt')
        ) 