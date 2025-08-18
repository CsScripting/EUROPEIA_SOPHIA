# This file makes "entities" a package

from .event import Event, EventApiDTO
from .module import Module, ModuleDTO
from .scientific_area import ScientificArea, ScientificAreaDTO
from .week import Week, WeekDTO
from .event_type import EventType, EventTypeDTO
from .academic_year import AcademicYear, AcademicYearDTO
from .classroom import Classroom, ClassroomDTO
from .building import Building, BuildingDTO
from .floor import Floor, FloorDTO
from .characteristic import Characteristic, CharacteristicDTO
from .campus import Campus, CampusDTO
from .course import Course, CourseDTO
from .curricular_plan import CurricularPlan, CurricularPlanDTO
from .student_group import StudentGroup, StudentGroupDTO
from .category import Category, CategoryDTO
from .labour_contract import LabourContract, LabourContractDTO
from .teacher import Teacher, TeacherDTO
from .typology import Typology, TypologyDTO

__all__ = [
    "Event", "EventApiDTO",
    "Module", "ModuleDTO",
    "ScientificArea", "ScientificAreaDTO",
    "Week", "WeekDTO",
    "EventType", "EventTypeDTO",
    "AcademicYear", "AcademicYearDTO",
    "Classroom", "ClassroomDTO",
    "Building", "BuildingDTO",
    "Floor", "FloorDTO",
    "Characteristic", "CharacteristicDTO",
    "Campus", "CampusDTO",
    "Course", "CourseDTO",
    "CurricularPlan", "CurricularPlanDTO",
    "StudentGroup", "StudentGroupDTO",
    "Category", "CategoryDTO",
    "LabourContract", "LabourContractDTO",
    "Teacher", "TeacherDTO",
    "Typology", "TypologyDTO",
] 