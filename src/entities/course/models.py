from dataclasses import dataclass
from typing import Optional
from .dto import CourseDTO

@dataclass
class Course:
    """
    Represents a Course entity.

    This class defines an academic course, which can have multiple
    curricular plans associated with it.
    """
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
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dto(cls, dto: CourseDTO) -> 'Course':
        return cls(
            id=dto.id,
            name=dto.name,
            code=dto.code,
            acronym=dto.acronym,
            color=dto.color,
            active=dto.active,
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> CourseDTO:
        return CourseDTO(
            id=self.id,
            name=self.name,
            code=self.code,
            acronym=self.acronym,
            color=self.color,
            active=self.active,
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        ) 