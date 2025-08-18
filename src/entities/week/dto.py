from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class WeekDTO:
    # Mandatory fields
    startDate: str

    # Optional fields
    id: Optional[int] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None 

    @classmethod
    def from_dict(cls, data: dict) -> 'WeekDTO':
        """Creates a WeekDTO instance from a dictionary."""
        if not data:
            raise ValueError("Input data is None or empty, cannot create WeekDTO with mandatory fields.")

        # Check for mandatory fields
        if 'startDate' not in data:
            raise ValueError("Missing mandatory field 'startDate' to create WeekDTO from dict")

        return cls(
            startDate=data['startDate'],
            id=data.get('id'),
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt')
        ) 