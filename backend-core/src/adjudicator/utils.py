import hashlib
from typing import List
from .models import Participant, TraceStep


def normalize_seed_to_int(seed_text: str) -> int:
    """
    Normaliza una semilla textual arbitraria a un entero grande determinista.
    Usamos SHA-256 y lo convertimos a entero.
    """
    digest = hashlib.sha256(seed_text.encode("utf-8")).digest()
    return int.from_bytes(digest, byteorder="big")


def build_base_seed(session_id: str, public_seed: str) -> str:
    """
    Construye una "semilla base" combinando la sesión y la semilla pública.
    Esto evita reutilizar directamente la semilla externa tal cual.
    """
    return f"{session_id}|{public_seed}"


def sort_participants_deterministically(participants: List[Participant]) -> List[Participant]:
    """
    Ordena los participantes de forma determinista.
    Aquí elegimos: primero por ticket_number, luego por participant_id.
    """
    return sorted(
        participants,
        key=lambda p: (p.ticket_number, p.participant_id)
    )


def create_trace_step(step: int, description: str, value: str) -> TraceStep:
    return TraceStep(step=step, description=description, value=value)
