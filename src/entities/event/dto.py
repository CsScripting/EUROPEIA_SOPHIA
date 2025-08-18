from dataclasses import dataclass, field, asdict
from typing import Any, List, Optional
from enum import IntEnum

# Import DTOs from other entity packages
from ..module.dto import ModuleDTO
from ..week.dto import WeekDTO
from ..event_type.dto import EventTypeDTO
from ..academic_year.dto import AcademicYearDTO
from ..classroom.dto import ClassroomDTO
from ..student_group.dto import StudentGroupDTO
from ..teacher.dto import TeacherDTO
from ..typology.dto import TypologyDTO
from src.variables.mod_variables import *

# Enum for Day
class DayOfWeekEnum(IntEnum):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6

# Placeholder DTOs still needed directly by EventDTO.
# These will remain here until they are promoted to their own full entity packages.
@dataclass
class ThirdPartyEventClientDTO:
    # Define fields for ThirdPartyEventClientDTO here
    eventId: Optional[str] = None # Assuming string, adjust if int or other
    clientId: Optional[str] = None # Assuming string
    stillThirdParty: Optional[bool] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ThirdPartyEventClientDTO':
        """Creates a ThirdPartyEventClientDTO instance from a dictionary."""
        if not data:
            return cls() # Return an empty/default instance if no data

        return cls(
            eventId=data.get('eventId'),
            clientId=data.get('clientId'),
            stillThirdParty=data.get('stillThirdParty'),
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt')
        )

@dataclass
class EventTicketEventDTO:
    # Define fields for EventTicketEventDTO here
    # Mandatory fields based on user input with *
    eventId: str # Assuming string, adjust if int or other
    eventTicketId: str # Assuming string

    # Optional fields
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'EventTicketEventDTO':
        """Creates an EventTicketEventDTO instance from a dictionary."""
        if not data:
            # For DTOs with mandatory fields, returning an empty instance might be problematic.
            # Consider raising an error or having a more sophisticated default if data is None/empty.
            raise ValueError("Input data is None or empty, cannot create EventTicketEventDTO with mandatory fields.")

        # Check for mandatory fields
        if 'eventId' not in data or 'eventTicketId' not in data:
            raise ValueError("Missing one or more mandatory fields (eventId, eventTicketId) to create EventTicketEventDTO from dict")

        return cls(
            eventId=data['eventId'],
            eventTicketId=data['eventTicketId'],
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt')
        )

@dataclass
class EventApiDTO:
    # Mandatory fields
    startTime: str
    endTime: str
    duration: str
    day: DayOfWeekEnum
    eventType: EventTypeDTO
    numStudents: int
    wlsSectionName: str
    wlsSectionConnector: str
    annotations: str

    # Optional fields
    id: Optional[int] = None
    name: Optional[str] = None
    isOwner: Optional[bool] = None
    unit: Optional[str] = None
    weeks: List[WeekDTO] = field(default_factory=list)
    classrooms: List[ClassroomDTO] = field(default_factory=list)
    usersEventRole: List[Any] = field(default_factory=list)
    studentGroups: List[StudentGroupDTO] = field(default_factory=list)
    teachers: List[TeacherDTO] = field(default_factory=list)
    module: Optional[ModuleDTO] = None
    typologies: List[TypologyDTO] = field(default_factory=list)
    academicYear: Optional[AcademicYearDTO] = None
    thirdPartyEventClient: Optional[ThirdPartyEventClientDTO] = None
    eventCompensationEvent: Optional[Any] = None
    eventTicketEvent: Optional[EventTicketEventDTO] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'EventApiDTO':
        """Creates an EventApiDTO instance from a dictionary, handling nested DTOs and lists of DTOs."""
        if not data:
            raise ValueError("Input data is None or empty, cannot create EventApiDTO with mandatory fields.")

        # Check for mandatory fields for EventApiDTO itself
        mandatory_event_fields = [
            'startTime', 'endTime', 'duration', 'day', 'eventType',
            'numStudents', 'wlsSectionName', 'wlsSectionConnector', 'annotations'
        ]
        for field_name in mandatory_event_fields:
            if field_name not in data:
                raise ValueError(f"Missing mandatory field '{field_name}' for EventApiDTO from dict")

        # --- Handle DTO aninhada obrigatória: eventType ---
        event_type_data = data['eventType'] # Already checked for presence
        if not isinstance(event_type_data, dict):
            raise ValueError("Field 'eventType' must be a dictionary for EventApiDTO.")
        event_type_dto = EventTypeDTO.from_dict(event_type_data)

        # --- Handle DTOs aninhadas opcionais ---
        module_dto = None
        module_data = data.get('module')
        if module_data is not None:
            if isinstance(module_data, dict):
                module_dto = ModuleDTO.from_dict(module_data)
            else:
                raise ValueError("Field 'module' is present but not a dictionary for EventApiDTO.")

        academic_year_dto = None
        academic_year_data = data.get('academicYear')
        if academic_year_data is not None:
            if isinstance(academic_year_data, dict):
                academic_year_dto = AcademicYearDTO.from_dict(academic_year_data)
            else:
                raise ValueError("Field 'academicYear' is present but not a dictionary for EventApiDTO.")

        third_party_client_dto = None
        third_party_data = data.get('thirdPartyEventClient')
        if third_party_data is not None:
            if isinstance(third_party_data, dict):
                third_party_client_dto = ThirdPartyEventClientDTO.from_dict(third_party_data)
            else:
                raise ValueError("Field 'thirdPartyEventClient' is present but not a dictionary for EventApiDTO.")

        event_ticket_dto = None
        event_ticket_data = data.get('eventTicketEvent')
        if event_ticket_data is not None:
            if isinstance(event_ticket_data, dict):
                event_ticket_dto = EventTicketEventDTO.from_dict(event_ticket_data)
            else:
                raise ValueError("Field 'eventTicketEvent' is present but not a dictionary for EventApiDTO.")

        # --- Handle listas de DTOs ---
        weeks_dto_list = []
        weeks_list_data = data.get('weeks', [])
        if not isinstance(weeks_list_data, list):
            raise ValueError("Field 'weeks' must be a list for EventApiDTO.")
        for week_item_data in weeks_list_data:
            if isinstance(week_item_data, dict):
                weeks_dto_list.append(WeekDTO.from_dict(week_item_data))
            else:
                raise ValueError("Item in 'weeks' list is not a dictionary for EventApiDTO.")

        classrooms_dto_list = []
        classrooms_list_data = data.get('classrooms', [])
        if not isinstance(classrooms_list_data, list):
            raise ValueError("Field 'classrooms' must be a list for EventApiDTO.")
        for classroom_item_data in classrooms_list_data:
            if isinstance(classroom_item_data, dict):
                classrooms_dto_list.append(ClassroomDTO.from_dict(classroom_item_data))
            else:
                raise ValueError("Item in 'classrooms' list is not a dictionary for EventApiDTO.")

        student_groups_dto_list = []
        student_groups_list_data = data.get('studentGroups', [])
        if not isinstance(student_groups_list_data, list):
            raise ValueError("Field 'studentGroups' must be a list for EventApiDTO.")
        for sg_item_data in student_groups_list_data:
            if isinstance(sg_item_data, dict):
                student_groups_dto_list.append(StudentGroupDTO.from_dict(sg_item_data))
            else:
                raise ValueError("Item in 'studentGroups' list is not a dictionary for EventApiDTO.")

        teachers_dto_list = []
        teachers_list_data = data.get('teachers', [])
        if not isinstance(teachers_list_data, list):
            raise ValueError("Field 'teachers' must be a list for EventApiDTO.")
        for teacher_item_data in teachers_list_data:
            if isinstance(teacher_item_data, dict):
                teachers_dto_list.append(TeacherDTO.from_dict(teacher_item_data))
            else:
                raise ValueError("Item in 'teachers' list is not a dictionary for EventApiDTO.")

        typologies_dto_list = []
        typologies_list_data = data.get('typologies', [])
        if not isinstance(typologies_list_data, list):
            raise ValueError("Field 'typologies' must be a list for EventApiDTO.")
        for typology_item_data in typologies_list_data:
            if isinstance(typology_item_data, dict):
                typologies_dto_list.append(TypologyDTO.from_dict(typology_item_data))
            else:
                raise ValueError("Item in 'typologies' list is not a dictionary for EventApiDTO.")

        # --- Handle Enum: day ---
        day_value = data['day']
        try:
            day_enum = DayOfWeekEnum(day_value) # Assumes API sends integer compatible with Enum
        except ValueError as e:
            # If API sends string like "MONDAY", we might need DayOfWeekEnum[data['day']] if names match
            # Or a mapping if API values differ significantly from Enum names/values
            raise ValueError(f"Invalid value for 'day': {day_value}. Cannot convert to DayOfWeekEnum. Error: {e}")

        # --- Criar a instância da EventApiDTO ---
        return cls(
            startTime=data['startTime'],
            endTime=data['endTime'],
            duration=data['duration'],
            day=day_enum,
            eventType=event_type_dto,
            numStudents=data['numStudents'],
            wlsSectionName=data['wlsSectionName'],
            wlsSectionConnector=data['wlsSectionConnector'],
            annotations=data['annotations'],
            
            id=data.get('id'),
            name=data.get('name'),
            isOwner=data.get('isOwner'),
            unit=data.get('unit'),
            
            weeks=weeks_dto_list,
            classrooms=classrooms_dto_list,
            usersEventRole=data.get('usersEventRole', []),
            studentGroups=student_groups_dto_list,
            teachers=teachers_dto_list,
            module=module_dto,
            typologies=typologies_dto_list,
            academicYear=academic_year_dto,
            thirdPartyEventClient=third_party_client_dto,
            eventCompensationEvent=data.get('eventCompensationEvent'), # Assuming direct pass-through for Any type
            eventTicketEvent=event_ticket_dto,
            
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt')
        )

# --- EventViewerDTO Definition starts here ---
# (Conteúdo de src/entities/event/viewer_dto.py será colado aqui, 
#  removendo as suas próprias importações de DayOfWeekEnum pois já está definido acima)

@dataclass
class EventViewerDTO:
    """
    DTO para visualização de dados de Eventos, com campos selecionados e achatados
    para fácil exportação e análise (e.g., para Excel).
    Os campos `*_id`, `*_name`, `*_code` são extraídos de objetos relacionados.
    Campos de listas de objetos (como weeks, teachers) são concatenados em strings.
    """
    # DayOfWeekEnum já está definido neste ficheiro, não precisa de importação local.
    
    startTime: Optional[str] = None 
    endTime: Optional[str] = None   

    id: Optional[int] = None
    name: Optional[str] = None
    duration: Optional[str] = None
    day: Optional[DayOfWeekEnum] = None
    wlsSectionName: Optional[str] = None
    wlsSectionConnector: Optional[str] = None 
    unit: Optional[str] = None
    annotations: Optional[str] = None
    numStudents: Optional[int] = None

    eventType_id: Optional[int] = None
    eventType_name: Optional[str] = None
    

    module_id: Optional[int] = None 
    module_name: Optional[str] = None
    module_code: Optional[str] = None
    module_acronym: Optional[str] = None

    academicYear_id: Optional[int] = None
    academicYear_name: Optional[str] = None

    week_ids: Optional[str] = None
    week_startDates: Optional[str] = None
    

    classroom_ids: Optional[str] = None
    classroom_names: Optional[str] = None
    classroom_codes: Optional[str] = None

    studentGroup_ids: Optional[str] = None
    studentGroup_names: Optional[str] = None
    studentGroup_codes: Optional[str] = None

    # Planos
    plan_ids: Optional[List[str]] = None
    plan_names: Optional[List[str]] = None
    plan_codes: Optional[List[str]] = None

    # Cursos
    course_ids: Optional[List[str]] = None
    course_names: Optional[List[str]] = None
    course_codes: Optional[List[str]] = None
    course_acronyms: Optional[List[str]] = None
    

    teacher_ids: Optional[str] = None
    teacher_names: Optional[str] = None
    teacher_codes: Optional[str] = None
    
    typology_ids: Optional[str] = None 
    typology_names: Optional[str] = None

    
    

# --- DTOs for constructing specific event payload structures (e.g., for create operations) ---

@dataclass
class NestedIdentifierStatusDTO:
    """Representa uma estrutura aninhada como {"model": {"identifier": "value"}, "status": 1}."""
    model: dict[str, Any]  # Deve ser {'identifier': 'algum_valor'}
    status: int

@dataclass
class InsertEventPayloadStructureDTO:
    """
    Representa a estrutura de um único payload de evento para criação.
    Os nomes dos campos são derivados das necessidades comuns para criar um evento.
    """
    # Campos obrigatórios
    # APENAS COMO OPCIONAIS PARA Iniciar OBJETO E MAIS TARDE PREENCHER
    name: Optional[str] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    day: Optional[int] = None
    wlsSectionName: Optional[str] = None
    wlsSectionConnector: Optional[str] = None
    eventTypeId: Optional[int] = None
    moduleId: Optional[int] = None
    academicYearId: Optional[int] = None
    numStudents: Optional[int] = None

    # Campos opcionais
    unit: Optional[str] = None
    annotations: Optional[str] = None
    eventUsersRole: List[Any] = field(default_factory=list)

    weeks: List[NestedIdentifierStatusDTO] = field(default_factory=list)
    studentGroups: List[NestedIdentifierStatusDTO] = field(default_factory=list)
    teachers: List[NestedIdentifierStatusDTO] = field(default_factory=list)
    classrooms: List[NestedIdentifierStatusDTO] = field(default_factory=list)
    typologies: List[NestedIdentifierStatusDTO] = field(default_factory=list)

    # eventConstraints: Optional[bool] = None # Placeholder se necessário

    @classmethod
    def get_mandatory_dataFrame_fields(cls) -> List[str]:
        """
        Retorna uma lista dos nomes das colunas do Excel que correspondem 
        aos campos obrigatórios desta DTO.
        Estes nomes devem estar alinhados com as constantes COL_EXCEL_* usadas no script principal.
        """
        return [
            'event_name',          # Mapeia para DTO.name
            'startTime',           # Mapeia para DTO.startTime
            'endTime',             # Mapeia para DTO.endTime
            'day',                 # Mapeia para DTO.day
            'wlsSectionName',      # Mapeia para DTO.wlsSectionName
            'wlsSectionConnector', # Mapeia para DTO.wlsSectionConnector
            'eventTypeId',        # Mapeia para DTO.eventTypeId
            'module_id',           # Mapeia para DTO.moduleId
            'academicYear_id',     # Mapeia para DTO.academicYearId
            'numStudents'          # Mapeia para DTO.numStudents
        ]

    def to_dict(self) -> dict[str, Any]:
        """Converte o DTO para um dicionário, filtrando valores None."""
        return asdict(self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})
    
    @classmethod
    def data_uxxi_to_data_object_event(cls) -> dict[str, str]:
        """
        Converte dados de UXXI para um objeto Event.
        """
        columns_to_map = {
            v_event_Id_BC : 'event_name',
            v_mod_id_dominant : 'module_id',
            v_mod_name : 'module_name',
            v_mod_code_dominant : 'module_code',
            v_mod_typologie : 'typology_name',
            v_mod_id_typologie : 'typology_id',
            v_hourBegin : 'startTime',
            v_hourEnd : 'endTime',
            v_day : 'day',
            v_students_number : 'numStudents',
            v_weeks : 'week_startDates',
            v_id_weeks : 'week_ids',
            
            v_event_type : 'eventType_name',
            v_id_event_type : 'eventType_id',
            v_section_name : 'wlsSectionName',
            v_id_uxxi : 'wlsSectionConnector',
            v_annotation_event : 'annotations',
            
            v_academic_year : 'academicYear_name',
            v_id_academic_year : 'academicYear_id',

            v_student_group_id_best : 'studentGroup_ids',
            v_student_group_best : 'studentGroup_names',

            

            
            
        }
    
        return columns_to_map
    @classmethod
    def get_field_names_insert_event_without_teacher_classroom(cls) -> list[str]:
        """
        Retorna uma lista com os nomes de todos os campos definidos nesta DTO.
        Útil para selecionar colunas de um DataFrame.
        """
        return [
            
            'event_name',
            'module_id',
            'module_name',
            'module_code',
            'typology_id',
            'typology_name',
            'startTime',
            'endTime',
            'day',
            'numStudents',
            'week_ids',
            'week_startDates',
            'eventType_id',
            'eventType_name',
            'wlsSectionName',
            'wlsSectionConnector',
            'annotations',
            'academicYear_id',
            'academicYear_name',
            'studentGroup_ids',
            'studentGroup_names',
            
        ]



@dataclass
class DeleteEventPayloadStructureDTO:
    """
    Representa a estrutura de um único payload de evento eliminar evento
    """
    # Campos obrigatórios
    # APENAS COMO OPCIONAIS PARA Iniciar OBJETO E MAIS TARDE PREENCHER
    id: Optional[int]

    def to_dict(self) -> int:
        """Converte o DTO para um inteiro (o ID do evento)."""
        if self.id is None:
            raise ValueError("ID cannot be None when creating a delete payload.")
        return self.id


@dataclass
class UpdateEventPayloadStructureDTO(InsertEventPayloadStructureDTO):
    """
    Representa a estrutura de um único payload de evento, como gerado pela função create_dto_event do utilizador,
    destinado a coleções como eventsCreateCollection ou para atualizações.
    Herda campos comuns de InsertEventPayloadStructureDTO e adiciona um 'id'.
    """
    
    id: Optional[int] = None 

@dataclass
class CreateEventFromSectionBTT:
    """
    DTO para representar os dados de uma secção BTT, tipicamente lidos de uma fonte externa como Excel.
    Todos os campos são opcionais por defeito.
    """
    wload_id: Optional[int] = None
    wload_name: Optional[str] = None
    module_id: Optional[int] = None
    module_name: Optional[str] = None
    module_code: Optional[str] = None
    academic_term_slot: Optional[str] = None # Ou int, dependendo do formato
    wload_typologies_num_slots: Optional[int] = None
    typology_ids: Optional[str] = None         # Assumindo string de IDs separados por vírgula
    typology_names: Optional[str] = None       # Assumindo string de nomes separados por vírgula
    week_ids: Optional[str] = None             # Assumindo string de IDs separados por vírgula
    week_startDates: Optional[str] = None    # Assumindo string de datas separadas por vírgula
    wl_session_id: Optional[int] = None
    wl_session_name: Optional[str] = None
    wls_section_id: Optional[int] = None
    wlsSectionName: Optional[str] = None
    wls_section_num_students: Optional[int] = None
    wlsSectionConnector: Optional[str] = None
    studentGroup_ids: Optional[str] = None     # Assumindo string de IDs separados por vírgula
    studentGroup_names: Optional[str] = None   # Assumindo string de nomes separados por vírgula
    teacher_ids: Optional[str] = None          # Assumindo string de IDs separados por vírgula
    teacher_names: Optional[str] = None        # Assumindo string de nomes separados por vírgula
    teacher_codes: Optional[str] = None        # Assumindo string de códigos separados por vírgula

    
    @classmethod
    def get_field_names(cls) -> list[str]:
        """
        Retorna uma lista com os nomes de todos os campos definidos nesta DTO.
        Útil para selecionar colunas de um DataFrame.
        """
        return [
            
            'module_id',
            'module_name',
            'module_code',
            'typology_ids',
            'typology_names',
            'week_ids',
            'week_startDates',
            'wls_section_id',
            'wlsSectionName',
            'wload_typologies_num_slots',
            'wls_section_num_students',
            'wlsSectionConnector',
            'studentGroup_ids',
            'studentGroup_names',
            'teacher_ids',
            'teacher_names',
            'teacher_codes'
        ]
    
    
    
    @classmethod
    def get_excel_column_mapping(cls) -> dict[str, str]:
        """
        Retorna um dicionário para mapear nomes de colunas do Excel (chaves)
        para nomes de campos da DTO CreateEventFromSectionBTT (valores).
        Este mapa deve ser preenchido com os nomes reais das colunas do seu Excel.
        """
        # Preencha este dicionário com o mapeamento real:
        # Exemplo: { 'Nome da Coluna no Excel': 'nome_do_campo_na_dto', ... }
        excel_to_dto_map = {

            'wls_section_num_students': 'numStudents',
            

        }
        return excel_to_dto_map
    

    
