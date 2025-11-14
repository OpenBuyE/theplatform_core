from typing import Tuple
import hashlib

from .models import (
    AdjudicationInput,
    AdjudicationResult,
    Participant,
    TraceStep,
)
from .utils import (
    normalize_seed_to_int,
    build_base_seed,
    sort_participants_deterministically,
    create_trace_step,
)


def _compute_winner_index(numeric_seed: int, total_participants: int) -> int:
    """
    Dado un entero grande (numeric_seed) y el número total de participantes N,
    el índice ganador es: numeric_seed mod N.
    """
    if total_participants <= 0:
        raise ValueError("No hay participantes en la sesión de adjudicación.")
    return numeric_seed % total_participants


def _hash_result(session_id: str, winner_participant_id: str, numeric_seed: int) -> str:
    """
    Genera un hash del resultado para facilitar verificaciones y sellado.
    """
    base = f"{session_id}|{winner_participant_id}|{numeric_seed}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def adjudicate_session(input_data: AdjudicationInput) -> AdjudicationResult:
    """
    Ejecuta el proceso de adjudicación determinista para una sesión cerrada.

    Pasos:
    1) Ordenar participantes de forma determinista.
    2) Construir una semilla base combinando session_id + public_seed.
    3) Normalizar esa semilla base a un entero mediante SHA-256.
    4) Calcular winner_index = numeric_seed % N.
    5) Seleccionar el participante ganador.
    6) Generar una traza explicativa.
    7) Devolver AdjudicationResult.
    """

    trace = []

    # Paso 1: ordenar participantes
    trace.append(create_trace_step(
        step=1,
        description="Número de participantes en la sesión",
        value=str(len(input_data.participants))
    ))

    ordered_participants = sort_participants_deterministically(input_data.participants)
    if not ordered_participants:
        raise ValueError("La lista de participantes está vacía.")

    # Paso 2: construir semilla base
    base_seed = build_base_seed(
        session_id=input_data.session_id,
        public_seed=input_data.public_seed
    )
    trace.append(create_trace_step(
        step=2,
        description="Semilla base (session_id | public_seed)",
        value=base_seed
    ))

    # Paso 3: normalizar semilla a entero
    numeric_seed = normalize_seed_to_int(base_seed)
    trace.append(create_trace_step(
        step=3,
        description="Semilla numérica (SHA-256 → entero)",
        value=str(numeric_seed)
    ))

    # Paso 4: calcular índice ganador
    winner_index = _compute_winner_index(numeric_seed, len(ordered_participants))
    trace.append(create_trace_step(
        step=4,
        description="Índice ganador (numeric_seed mod N)",
        value=f"{winner_index} (N={len(ordered_participants)})"
    ))

    # Paso 5: seleccionar participante ganador
    winner: Participant = ordered_participants[winner_index]
    trace.append(create_trace_step(
        step=5,
        description="Participante ganador (según índice ganador en lista ordenada)",
        value=f"participant_id={winner.participant_id}, ticket_number={winner.ticket_number}"
    ))

    # Paso 6: generar hash del resultado
    result_hash = _hash_result(
        session_id=input_data.session_id,
        winner_participant_id=winner.participant_id,
        numeric_seed=numeric_seed
    )
    trace.append(create_trace_step(
        step=6,
        description="Hash del resultado (session_id | winner_id | numeric_seed)",
        value=result_hash
    ))

    # Paso 7: construir objeto resultado
    result = AdjudicationResult(
        session_id=input_data.session_id,
        product_id=input_data.product_id,
        group_id=input_data.group_id,
        algorithm_version=input_data.algorithm_version,
        public_seed=input_data.public_seed,
        numeric_seed=numeric_seed,
        winner_participant_id=winner.participant_id,
        winner_ticket_number=winner.ticket_number,
        winner_index=winner_index,
        trace=trace,
        result_hash=result_hash,
    )

    return result
