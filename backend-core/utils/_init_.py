from typing import List, Optional

from .helpers import generate_uuid, current_timestamp
from .validators import is_valid_uuid, ensure_positive_number
from .crypto import sha256
from .logger import log

from models.adjudication import Participant, TraceStep


def build_base_seed(
    session_id: str,
    closing_timestamp: str,
    participant_ids_concat: str,
    public_seed: Optional[str] = None,
) -> str:
    """
    Construye la semilla base a partir de:
    - session_id
    - closing_timestamp
    - concatenación de IDs de participantes (en orden determinista)
    - opcionalmente una semilla pública (drand, etc.)

    Esto refleja fielmente tu memoria técnica:
    HASH = SHA256( session_id + timestamp_cierre + ids_participantes_concatenados [+ public_seed] )
    """
    components = [session_id, closing_timestamp, participant_ids_concat]
    if public_seed:
        components.append(public_seed)
    return "|".join(components)


def normalize_seed_to_int(base_seed: str) -> int:
    """
    SHA-256 de la semilla base → entero (base 16).
    """
    digest = sha256(base_seed)
    return int(digest, 16)


def sort_participants_deterministically(participants: List[Participant]) -> List[Participant]:
    """
    Orden determinista de participantes.

    Siguiendo tu criterio:
    - Primero por join_timestamp (si existe)
    - Luego por ticket_number
    - Luego por participant_id

    Eso garantiza que, dado el mismo conjunto de participantes,
    cualquier implementación ordenará igual.
    """
    return sorted(
        participants,
        key=lambda p: (
            p.join_timestamp or "",
            str(p.ticket_number).zfill(10),
            p.participant_id,
        ),
    )


def create_trace_step(step: int, description: str, value: str) -> TraceStep:
    """
    Crea un paso de traza legible y estructurado.
    """
    return TraceStep(step=step, description=description, value=value)

