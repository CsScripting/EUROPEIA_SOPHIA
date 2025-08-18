from dataclasses import dataclass
from typing import Optional
from ..curricular_plan.dto import CurricularPlanDTO

@dataclass
class StudentGroupDTO:
    # Mandatory fields
    name: str
    numStudents: int
    dayLimit: int # Assuming int, adjust if it's a specific type like timedelta or str
    consecutiveLimit: int # Assuming int
    active: bool

    # Optional fields
    id: Optional[int] = None
    observations: Optional[str] = None
    code: Optional[str] = None
    curricularPlan: Optional[CurricularPlanDTO] = None # This will be a CurricularPlanDTO instance
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None # Consider datetime object or ISO string
    createdAt: Optional[str] = None      # Consider datetime object or ISO string 

    @classmethod
    def from_dict(cls, data: dict) -> 'StudentGroupDTO':
        """Creates a StudentGroupDTO instance from a dictionary."""
        if not data:
            raise ValueError("Input data is None or empty, cannot create StudentGroupDTO with mandatory fields.")

        # Check for mandatory fields
        mandatory_fields = ['name', 'numStudents', 'dayLimit', 'consecutiveLimit', 'active']
        for field_name in mandatory_fields:
            if field_name not in data:
                raise ValueError(f"Missing mandatory field '{field_name}' to create StudentGroupDTO from dict")

        # Handle nested CurricularPlanDTO
        curricular_plan_data = data.get('curricularPlan')
        curricular_plan_dto: Optional[CurricularPlanDTO] = None
        if curricular_plan_data is not None:
            if isinstance(curricular_plan_data, dict):
                curricular_plan_dto = CurricularPlanDTO.from_dict(curricular_plan_data)
            else:
                raise ValueError("Field 'curricularPlan' is present but not a dictionary.")

        return cls(
            name=data['name'],
            numStudents=data['numStudents'],
            dayLimit=data['dayLimit'],
            consecutiveLimit=data['consecutiveLimit'],
            active=data['active'],
            id=data.get('id'),
            observations=data.get('observations'),
            code=data.get('code'),
            curricularPlan=curricular_plan_dto,
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt')
        ) 