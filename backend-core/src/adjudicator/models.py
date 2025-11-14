from typing import List, Optional
from pydantic import BaseModel, Field


class Participant(BaseModel):
    """
    Representa a un participante dentro de una sesión de compra colectiva.
    """
    participant_id: str = Field(..., description="Identificador interno del participante")
    ticket_number: int = Field(..., description="Número de participación dentro del grupo (1..N)")
    weight: float = Field(1.0, description="Peso opcional (por defecto 1.0; normalmente no se usa)")


class AdjudicationInput(BaseModel):
    """
    Entrada canónica para el proceso de adjudicación.
    """
    session_id: str = Field(..., description="Identificador único de la sesión de compra colectiva")
    product_id: str = Field(..., description="Identificador del producto asociado a la sesión")
    group_id: str = Field(..., description="Identificador lógico del grupo (por país / operador, etc.)")

    # Semilla de aleatoriedad pública/verificable (ej. hash de beacon, drand, fintech, etc.)
    public_seed: str = Field(..., description="Semilla pública de aleatoriedad (en formato texto)")

    # Lista de participantes (ya cerrada, no modificable)
    participants: List[Participant] = Field(..., description="Lista de participantes admitidos en la sesión")

    # Versión del algoritmo (para trazabilidad futura)
    algorithm_version: str = Field("1.0", description="Versión del algoritmo determinista de adjudicación")


class TraceStep(BaseModel):
    """
    Paso intermedio de la traza matemática, útil para auditoría y transparencia.
    """
    step: int
    description: str
    value: str


class AdjudicationResult(BaseModel):
    """
    Resultado completo del proceso de adjudicación.
    """
    session_id: str
    product_id: str
    group_id: str

    algorithm_version: str
    public_seed: str
    numeric_seed: int

    winner_participant_id: str
    winner_ticket_number: int

    # Índice interno usado (0..N-1) para seleccionar dentro de la lista ordenada
    winner_index: int

    # Trazabilidad detallada
    trace: List[TraceStep]

    # Campo opcional para anexar firma digital o hash del resultado
    result_hash: Optional[str] = None
