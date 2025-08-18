from dataclasses import dataclass
from typing import Optional
from .dto import CharacteristicDTO

@dataclass
class Characteristic:
    """
    Represents a Characteristic entity.

    This class defines a characteristic that can be associated with
    other entities, such as classrooms (e.g., "has projector", "is lab").
    """
    # Mandatory fields
    name: str
    active: bool

    # Optional fields
    id: Optional[int] = None
    createdBy: Optional[str] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedAt: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_dto(cls, dto: CharacteristicDTO) -> 'Characteristic':
        return cls(
            id=dto.id,
            name=dto.name,
            active=dto.active,
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> CharacteristicDTO:
        return CharacteristicDTO(
            id=self.id,
            name=self.name,
            active=self.active,
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        ) 