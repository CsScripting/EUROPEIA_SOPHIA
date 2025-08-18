from dataclasses import dataclass
from typing import Optional
from ..course.dto import CourseDTO

@dataclass
class CurricularPlanDTO:
    # Mandatory fields
    code: str
    name: str
    year: int # Assuming year is an integer
    active: bool

    # Optional fields
    id: Optional[int] = None
    course: Optional[CourseDTO] = None # This will be a CourseDTO instance
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None # Consider datetime object or ISO string
    createdAt: Optional[str] = None      # Consider datetime object or ISO string 

    @classmethod
    def from_dict(cls, data: dict) -> 'CurricularPlanDTO':
        """Creates a CurricularPlanDTO instance from a dictionary."""
        if not data:
            raise ValueError("Input data is None or empty, cannot create CurricularPlanDTO with mandatory fields.")

        # Check for mandatory fields
        mandatory_fields = ['code', 'name', 'year', 'active']
        for field_name in mandatory_fields:
            if field_name not in data:
                raise ValueError(f"Missing mandatory field '{field_name}' to create CurricularPlanDTO from dict")

        # Handle nested CourseDTO
        course_data = data.get('course')
        course_dto: Optional[CourseDTO] = None
        if course_data is not None:
            if isinstance(course_data, dict):
                course_dto = CourseDTO.from_dict(course_data)
            else:
                raise ValueError("Field 'course' is present but not a dictionary.")

        return cls(
            code=data['code'],
            name=data['name'],
            year=data['year'],
            active=data['active'],
            id=data.get('id'),
            course=course_dto,
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt')
        ) 