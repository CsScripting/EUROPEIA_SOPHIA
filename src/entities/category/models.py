from dataclasses import dataclass
from typing import Optional
from .dto import CategoryDTO

@dataclass
class Category:
    """
    Represents a Category entity.

    This class defines a category, often used to classify other entities
    such as teachers or staff.
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
    def from_dto(cls, dto: CategoryDTO) -> 'Category':
        return cls(
            id=dto.id,
            name=dto.name,
            active=dto.active,
            createdBy=dto.createdBy,
            lastModifiedBy=dto.lastModifiedBy,
            lastModifiedAt=dto.lastModifiedAt,
            createdAt=dto.createdAt
        )

    def to_dto(self) -> CategoryDTO:
        return CategoryDTO(
            id=self.id,
            name=self.name,
            active=self.active,
            createdBy=self.createdBy,
            lastModifiedBy=self.lastModifiedBy,
            lastModifiedAt=self.lastModifiedAt,
            createdAt=self.createdAt
        ) 