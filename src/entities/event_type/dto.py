from dataclasses import dataclass, field
from typing import Any, Optional, List

@dataclass
class EventTypeDTO:
    # Mandatory fields
    name: str
    color: str
    active: bool

    # Optional fields
    id: Optional[int] = None
    setToAplication: Optional[bool] = None
    resourceMetadataEntries: List[Any] = field(default_factory=list)
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'EventTypeDTO':
        """Creates an EventTypeDTO instance from a dictionary."""
        if not data: # Handle cases where data might be None or empty
            # Decide on behavior: raise error, return default, or return None
            # For now, let's assume valid data or raise error earlier if critical
            # Or, more gracefully:
            # return cls(name="DefaultName", color="#FFFFFF", active=False) # Example default
            # For robustness, let's assume if data is None/empty, it's an issue upstream
            # or the caller should handle it. If an empty DTO is desired, create it explicitly.
            # If a field is truly optional in source AND DTO, .get() handles it.
            # If mandatory in DTO but optional in source, error or default needed here.
            # Based on DTO definition, name, color, active are mandatory.
            if not all(k in data for k in ('name', 'color', 'active')):
                # Or handle more gracefully by creating a default or raising a specific error
                raise ValueError("Missing one or more mandatory fields (name, color, active) to create EventTypeDTO from dict")

        return cls(
            name=data['name'],
            color=data['color'],
            active=data['active'],
            id=data.get('id'),
            setToAplication=data.get('setToAplication'),
            resourceMetadataEntries=data.get('resourceMetadataEntries', []), # Default to empty list if not present
            createdBy=data.get('createdBy'),
            lastModifiedBy=data.get('lastModifiedBy'),
            lastModifiedAt=data.get('lastModifiedAt'),
            createdAt=data.get('createdAt'),
            description=data.get('description')
        )

@dataclass
class ReadExcelDataEventType:
    """
    DTO to define the expected column names when reading Event Type related data from an Excel file.
    """
    
    @staticmethod
    def get_field_names() -> List[str]:
        """
        Returns the list of field names expected from the Excel sheet
        for event type related data.
        """
        return [
            "course_code",
            "course_name",
            "faculty_id",
            "name"
        ]

@dataclass
class EventTypeParcialDTO:
    """
    DTO para definir os campos de 'EventType' relevantes obtidos da API,
    especialmente para criar um DataFrame para processamento e merge.
    """
    id: int 
    name: str
    active: bool

    @classmethod
    def get_api_field_names(cls) -> list[str]:
        """
        Retorna a lista dos nomes dos campos como eles aparecem na API,
        para serem usados ao criar o DataFrame com Pandas.
        Os nomes aqui devem corresponder exatamente às chaves no JSON da API.
        """
        # Estes são os nomes das chaves que esperamos da API para estes campos.
        # Se a API usar nomes diferentes (ex: 'isActive' em vez de 'active'), ajuste aqui.
        return ['id', 'name', 'active']

