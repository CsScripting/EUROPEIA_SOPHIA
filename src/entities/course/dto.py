from dataclasses import dataclass
from typing import Optional

@dataclass
class CourseDTO:
    # Mandatory fields
    name: str
    code: str
    acronym: str
    active: bool

    # Optional fields
    id: Optional[int] = None
    color: Optional[str] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None # Consider datetime object or ISO string
    createdAt: Optional[str] = None      # Consider datetime object or ISO string 

    @classmethod
    def from_dict(cls, data: dict) -> 'CourseDTO':
        """Creates a CourseDTO instance from a dictionary."""
        if not data:
            raise ValueError("Input data is None or empty, cannot create CourseDTO with mandatory fields.")

        # Check for mandatory fields
        mandatory_fields = ['name', 'code', 'acronym', 'active']
        for field_name in mandatory_fields:
            if field_name not in data:
                raise ValueError(f"Missing mandatory field '{field_name}' to create CourseDTO from dict")

        return cls(
            name=data['name'],
            code=data['code'],
            acronym=data['acronym'],
            active=data['active'],
            id=data.get('id'),
            color=data.get('color'),
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt')
        ) 