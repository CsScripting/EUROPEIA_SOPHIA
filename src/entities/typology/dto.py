from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TypologyDTO:
    name: str
    color: str
    constAvoidPeriodTypology: str
    active: bool
    id: Optional[int] = None
    description: Optional[str] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'TypologyDTO':
        """Creates a TypologyDTO instance from a dictionary."""
        if not data:
            raise ValueError("Input data is None or empty, cannot create TypologyDTO with mandatory fields.")

        # Check for mandatory fields
        mandatory_fields = ['name', 'color', 'constAvoidPeriodTypology', 'active']
        for field_name in mandatory_fields:
            if field_name not in data:
                raise ValueError(f"Missing mandatory field '{field_name}' to create TypologyDTO from dict")

        return cls(
            name=data['name'],
            color=data['color'],
            constAvoidPeriodTypology=data['constAvoidPeriodTypology'],
            active=data['active'],
            id=data.get('id'),
            description=data.get('description'),
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt')
        ) 