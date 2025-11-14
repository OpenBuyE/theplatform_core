from pydantic import BaseModel, Field
from typing import List, Optional


class Participant(BaseModel):
    """
    Representa a un participante en una sesión de compra colectiva determinista.
    No hay azar: la posición del participante en la lista ordenada y la semilla
    determinan el resultado de forma reproducible.
    """
    participant_id: str = Field(..., description="ID único del participante (usuario o ticket)")
    ticket_number: int = Field(..., description="Número de ticket / posición dentro de la sesión")
    join_timestamp: Optional[str] = Field(
        None,
        description="Timestamp ISO de cuándo se unió el participante (para auditoría y ordenación)"
    )


class TraceStep(BaseModel):
    """
    Paso explicativo dentro de la traza del proceso de adjudicación.
    Permite auditar el cálculo paso a paso.
    """
    step: int
    description: str
    value: str


class AdjudicationInput(BaseModel):
    """
    Datos de entrada para el motor determinista de adjudicación.
    Todo lo necesario para que cualquier tercero pueda reproducir el resultado.
    """
    session_id: str
    product_id: str
    group_id: str
    algorithm_version: str = "1.0"

    # Momento de cierre de la sesión (parte de la semilla).
    closing_timestamp: str

    # Opcionalmente se puede añadir una semilla pública (drand u otra),
    # siempre que sea verificable y pública. No convierte el sistema en azar,
    # porque la combinación de todos los datos sigue siendo determinista.
    public_seed: Optional[str] = None

    participants: List[Participant]


class AdjudicationResult(BaseModel):
    """
    Resultado completo de una adjudicación determinista para una sesión.
    No es un sorteo ni un juego de azar: es el resultado de aplicar una función
    matemática reproducible sobre datos fijos.
    """
    session_id: str
    product_id: str
    group_id: str

    algorithm_version: str
    public_seed: Optional[str]

    # Semilla numérica derivada por SHA-256 → entero.
    numeric_seed: int

    # Ganador
    winner_participant_id: str
    winner_ticket_number: int
    winner_index: int  # posición en la lista ordenada de participantes

    # Trazabilidad y auditoría
    trace: List[TraceStep]
    result_hash: str  # hash (session_id | winner_id | numeric_seed)
