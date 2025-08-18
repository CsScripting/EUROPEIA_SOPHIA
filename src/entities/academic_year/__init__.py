# This file makes "academic_year" a package 

from .dto import AcademicYearDTO
from .models import AcademicYear

__all__ = [
    "AcademicYearDTO",
    "AcademicYear",
] 