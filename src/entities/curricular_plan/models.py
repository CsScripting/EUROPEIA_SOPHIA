from dataclasses import dataclass
from typing import Optional
from .dto import CurricularPlanDTO
from ..course.dto import CourseDTO # For type hinting, can also use Course model if preferred
# from ..course.models import Course # If you want to store Course model instance

@dataclass
class CurricularPlan:
    """
    Represents a Curricular Plan entity.

    This class defines the structure of a curricular plan, which is
    typically associated with a specific course.

    Relationships:
    - course: Optional[CourseDTO] (One-to-One, optional) - The course to which the curricular plan belongs.
    """
    # Mandatory fields
    code: str
    name: str
    year: int
    active: bool

    # Optional fields
    id: Optional[int] = None
    course: Optional[CourseDTO] = None # Storing as DTO, or use Course model
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dto(cls, dto: CurricularPlanDTO) -> 'CurricularPlan':
        # course_model = Course.from_dto(dto.course) if dto.course else None
        return cls(
            id=dto.id,
            code=dto.code,
            name=dto.name,
            year=dto.year,
            course=dto.course, # Directly use CourseDTO or convert to Course model
            active=dto.active,
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> CurricularPlanDTO:
        # course_dto = self.course.to_dto() if self.course else None
        return CurricularPlanDTO(
            id=self.id,
            code=self.code,
            name=self.name,
            year=self.year,
            course=self.course, # Directly use CourseDTO or convert from Course model
            active=self.active,
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        ) 