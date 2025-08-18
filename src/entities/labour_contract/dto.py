from dataclasses import dataclass
from typing import Optional

@dataclass
class LabourContractDTO:
    # Mandatory fields
    active: bool

    # Optional fields
    id: Optional[int] = None
    name: Optional[str] = None # Name is optional as per lack of '*'
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None 

    @classmethod
    def from_dict(cls, data: dict) -> 'LabourContractDTO':
        """Creates a LabourContractDTO instance from a dictionary."""
        if not data:
            raise ValueError("Input data is None or empty, cannot create LabourContractDTO with mandatory fields.")

        # Check for mandatory fields
        if 'active' not in data:
            raise ValueError("Missing mandatory field 'active' to create LabourContractDTO from dict")

        return cls(
            active=data['active'],
            id=data.get('id'),
            name=data.get('name'),
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt')
        ) 