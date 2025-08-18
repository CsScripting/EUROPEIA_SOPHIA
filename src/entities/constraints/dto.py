from dataclasses import dataclass

@dataclass
class ConstraintParcialDTO:
    """
    DTO para definir os campos de 'constraint' que são relevantes para o processamento de eventos.
    O método get_api_field_names() fornecerá os nomes das chaves da API para usar com Pandas.
    """
    id: int
    name: str
    break_value: bool  # Mapeia para a chave 'break' da API
    active: bool

    @classmethod
    def get_api_field_names(cls) -> list[str]:
        """
        Retorna a lista dos nomes dos campos como eles aparecem na API, 
        para serem usados ao criar o DataFrame com Pandas.
        """
        return ['id', 'name', 'break', 'active']


@dataclass
class PayloadStatusBreakDTO:
    """
    DTO para o payload de atualização do status (break/active) de constrangimentos.
    """
    break_status: bool  # Mapeia para a chave 'break' no JSON do payload
    active: bool
    entitiesIdentifiers: list[int]

    def to_dict(self) -> dict:
        """
        Converte a DTO para um dicionário, mapeando 'break_status' para 'break' na chave.
        """
        return {
            "break": self.break_status,
            "active": self.active,
            "entitiesIdentifiers": self.entitiesIdentifiers
        }


