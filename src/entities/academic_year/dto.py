from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class AcademicYearDTO:
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
    def from_dict(cls, data: dict) -> 'AcademicYearDTO':
        """Creates an AcademicYearDTO instance from a dictionary."""
        if not data:
            raise ValueError("Input data is None or empty, cannot create AcademicYearDTO with mandatory fields.")

        # Check for mandatory fields
        if 'active' not in data:
            raise ValueError("Missing mandatory field 'active' to create AcademicYearDTO from dict")

        return cls(
            active=data['active'],
            id=data.get('id'),
            name=data.get('name'),
            startDate=data.get('startDate'),
            endDate=data.get('endDate'),
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt')
        ) 