from dataclasses import dataclass
from typing import Optional
from .dto import StudentGroupDTO
from ..curricular_plan.dto import CurricularPlanDTO # For type hinting
# from ..curricular_plan.models import CurricularPlan # If storing CurricularPlan model

@dataclass
class StudentGroup:
    """
    Represents a Student Group entity.

    This class defines a group of students, typically associated with a
    specific curricular plan.

    Relationships:
    - curricularPlan: Optional[CurricularPlanDTO] (One-to-One, optional) - The curricular plan for the student group.
    """
    # Mandatory fields
    name: str
    numStudents: int
    dayLimit: int
    consecutiveLimit: int
    active: bool

    # Optional fields
    id: Optional[int] = None
    observations: Optional[str] = None
    code: Optional[str] = None
    curricularPlan: Optional[CurricularPlanDTO] = None # Storing as DTO
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dto(cls, dto: StudentGroupDTO) -> 'StudentGroup':
        # cp_model = CurricularPlan.from_dto(dto.curricularPlan) if dto.curricularPlan else None
        return cls(
            id=dto.id,
            name=dto.name,
            observations=dto.observations,
            numStudents=dto.numStudents,
            dayLimit=dto.dayLimit,
            consecutiveLimit=dto.consecutiveLimit,
            code=dto.code,
            curricularPlan=dto.curricularPlan, # Store DTO or convert to CurricularPlan model
            active=dto.active,
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> StudentGroupDTO:
        # cp_dto = self.curricularPlan.to_dto() if self.curricularPlan else None
        return StudentGroupDTO(
            id=self.id,
            name=self.name,
            observations=self.observations,
            numStudents=self.numStudents,
            dayLimit=self.dayLimit,
            consecutiveLimit=self.consecutiveLimit,
            code=self.code,
            curricularPlan=self.curricularPlan, # Store DTO or convert from CurricularPlan model
            active=self.active,
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        ) 