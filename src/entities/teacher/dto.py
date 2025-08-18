from dataclasses import dataclass, field
from typing import Optional, Any # Any for degreeImportance initially

from ..category.dto import CategoryDTO
from ..labour_contract.dto import LabourContractDTO
from ..scientific_area.dto import ScientificAreaDTO # Reusing ScientificAreaDTO

@dataclass
class TeacherDTO:
    # Mandatory fields
    name: str
    acronym: str
    code: str
    consecutiveLimit: int # Assuming int, adjust if different
    constFreeDays: int    # Assuming int, adjust if different
    dayLimit: int         # Assuming int, adjust if different
    freeDays: int         # Assuming int, adjust if different
    degreeImportance: Any # Define more specifically if possible (e.g., int, str, Enum)
    active: bool

    # Optional fields
    id: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    observations: Optional[str] = None
    category: Optional[CategoryDTO] = None
    labourContract: Optional[LabourContractDTO] = None
    scientificArea: Optional[ScientificAreaDTO] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None 

    @classmethod
    def from_dict(cls, data: dict) -> 'TeacherDTO':
        """Creates a TeacherDTO instance from a dictionary."""
        if not data:
            raise ValueError("Input data is None or empty, cannot create TeacherDTO with mandatory fields.")

        mandatory_fields = [
            'name', 'acronym', 'code', 'consecutiveLimit', 
            'constFreeDays', 'dayLimit', 'freeDays', 'degreeImportance', 'active'
        ]
        for field_name in mandatory_fields:
            if field_name not in data:
                raise ValueError(f"Missing mandatory field '{field_name}' to create TeacherDTO from dict")

        # Handle nested CategoryDTO (optional)
        category_data = data.get('category')
        category_dto: Optional[CategoryDTO] = None
        if category_data is not None:
            if isinstance(category_data, dict):
                category_dto = CategoryDTO.from_dict(category_data)
            else:
                raise ValueError("Field 'category' is present but not a dictionary.")

        # Handle nested LabourContractDTO (optional)
        labour_contract_data = data.get('labourContract')
        labour_contract_dto: Optional[LabourContractDTO] = None
        if labour_contract_data is not None:
            if isinstance(labour_contract_data, dict):
                labour_contract_dto = LabourContractDTO.from_dict(labour_contract_data)
            else:
                raise ValueError("Field 'labourContract' is present but not a dictionary.")

        # Handle nested ScientificAreaDTO (optional)
        scientific_area_data = data.get('scientificArea')
        scientific_area_dto: Optional[ScientificAreaDTO] = None
        if scientific_area_data is not None:
            if isinstance(scientific_area_data, dict):
                scientific_area_dto = ScientificAreaDTO.from_dict(scientific_area_data)
            else:
                raise ValueError("Field 'scientificArea' is present but not a dictionary.")

        return cls(
            name=data['name'],
            acronym=data['acronym'],
            code=data['code'],
            consecutiveLimit=data['consecutiveLimit'],
            constFreeDays=data['constFreeDays'],
            dayLimit=data['dayLimit'],
            freeDays=data['freeDays'],
            degreeImportance=data['degreeImportance'], # Assuming direct pass-through for Any type
            active=data['active'],
            id=data.get('id'),
            email=data.get('email'),
            phone=data.get('phone'),
            observations=data.get('observations'),
            category=category_dto,
            labourContract=labour_contract_dto,
            scientificArea=scientific_area_dto,
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt')
        ) 