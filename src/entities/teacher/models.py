from dataclasses import dataclass, field
from typing import Optional, Any

from .dto import TeacherDTO
from ..category.dto import CategoryDTO # Changed from model to DTO for consistency
from ..labour_contract.dto import LabourContractDTO # Changed from model to DTO
from ..scientific_area.dto import ScientificAreaDTO # Changed from model to DTO

@dataclass
class Teacher:
    """
    Represents a Teacher entity.

    This class defines a teacher, including their personal details, contractual
    information, and academic associations.

    Relationships:
    - category: Optional[CategoryDTO] - The category of the teacher.
    - labourContract: Optional[LabourContractDTO] - The labour contract of the teacher.
    - scientificArea: Optional[ScientificAreaDTO] - The scientific area of the teacher.
    """
    # Mandatory fields
    name: str
    acronym: str
    code: str
    consecutiveLimit: int
    constFreeDays: int
    dayLimit: int
    freeDays: int
    degreeImportance: Any
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
    def from_dto(cls, dto: TeacherDTO) -> 'Teacher':
        return cls(
            name=dto.name,
            acronym=dto.acronym,
            code=dto.code,
            consecutiveLimit=dto.consecutiveLimit,
            constFreeDays=dto.constFreeDays,
            dayLimit=dto.dayLimit,
            freeDays=dto.freeDays,
            degreeImportance=dto.degreeImportance,
            active=dto.active,
            id=dto.id,
            email=dto.email,
            phone=dto.phone,
            observations=dto.observations,
            category=dto.category, # Assuming DTO is stored directly
            labourContract=dto.labourContract, # Assuming DTO is stored directly
            scientificArea=dto.scientificArea, # Assuming DTO is stored directly
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> TeacherDTO:
        return TeacherDTO(
            name=self.name,
            acronym=self.acronym,
            code=self.code,
            consecutiveLimit=self.consecutiveLimit,
            constFreeDays=self.constFreeDays,
            dayLimit=self.dayLimit,
            freeDays=self.freeDays,
            degreeImportance=self.degreeImportance,
            active=self.active,
            id=self.id,
            email=self.email,
            phone=self.phone,
            observations=self.observations,
            category=self.category, # Assuming DTO is stored directly
            labourContract=self.labourContract, # Assuming DTO is stored directly
            scientificArea=self.scientificArea, # Assuming DTO is stored directly
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        ) 