from typing import List
import hashlib

from models.adjudication import (
    AdjudicationInput,
    AdjudicationResult,
    Participant,
    TraceStep,
)
from utils import (
    normalize_seed_to_int,
    build_base_seed,
    sort_participants_deterministically,
    create_trace_step,
    current_timestamp,
)


class AdjudicationEngine:
    """
    Motor de adjudicación determinista de The Platform.

    No implementa azar ni juegos de suerte.
    Dado el mismo AdjudicationInput, siempre produce el mismo AdjudicationResult.
    Cualquier tercero puede verificarlo con SHA-256 estándar.
    """

    def __init__(self, algorithm_version: str = "1.0"):
        self.algorithm_version = algorithm_version

    @staticmethod
    def _compute_winner_index(numeric_seed: int, total_participants: int) -> int:
        """
        Dado un entero grande (numeric_seed) y el número total de participantes N,
        el índice ganador es: numeric_seed mod N.
        """
        if total_participants <= 0:
            raise ValueError("No hay participantes en la sesión de adjudicación.")
        return numeric_seed % total_participants

    @staticmethod
    def _hash_result(session_id: str, winner_participant_id: str, numeric_seed: int) -> str:
        """
        Genera un hash del resultado para facilitar verificaciones y sellado.
        """
        base = f"{session_id}|{winner_participant_id}|{numeric_seed}"
        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    def adjudicate_session(self, input_data: AdjudicationInput) -> AdjudicationResult:
        """
        Ejecuta el proceso de adjudicación determinista para una sesión cerrada.

        Pasos:
        1) Ordenar participantes de forma determinista.
        2) Construir una semilla base combinando:
           - session_id
           - closing_timestamp
           - IDs de participantes concatenados (en ese orden)
           - opcionalmente public_seed
        3) Normalizar esa semilla base a un entero mediante SHA-256.
        4) Calcular winner_index = numeric_seed % N.
        5) Seleccionar el participante ganador.
        6) Generar una traza explicativa.
        7) Devolver AdjudicationResult.

        Este proceso es:
        - determinista
        - reproducible
        - verificable por terceros
        - no constituye un juego de azar.
        """

        trace: List[TraceStep] = []

        # Paso 1: información de participantes
        trace.append(
            create_trace_step(
                step=1,
                description="Número de participantes en la sesión",
                value=str(len(input_data.participants)),
            )
        )

        ordered_participants: List[Participant] = sort_participants_deterministically(
            input_data.participants
        )
        if not ordered_participants:
            raise ValueError("La lista de participantes está vacía.")

        trace.append(
            create_trace_step(
                step=2,
                description="Participantes ordenados de forma determinista",
                value="; ".join(
                    f"{p.participant_id}:{p.ticket_number}" for p in ordered_participants
                ),
            )
        )

        # Construir la cadena de IDs concatenados
        participant_ids_concat = "".join([p.participant_id for p in ordered_participants])

        # Paso 3: construir semilla base
        base_seed = build_base_seed(
            session_id=input_data.session_id,
            closing_timestamp=input_data.closing_timestamp,
            participant_ids_concat=participant_ids_concat,
            public_seed=input_data.public_seed,
        )
        trace.append(
            create_trace_step(
                step=3,
                description="Semilla base (session_id | closing_timestamp | ids_concatenados | [public_seed])",
                value=base_seed,
            )
        )

        # Paso 4: normalizar semilla a entero
        numeric_seed = normalize_seed_to_int(base_seed)
        trace.append(
            create_trace_step(
                step=4,
                description="Semilla numérica (SHA-256 → entero)",
                value=str(numeric_seed),
            )
        )

        # Paso 5: calcular índice ganador
        winner_index = self._compute_winner_index(numeric_seed, len(ordered_participants))
        trace.append(
            create_trace_step(
                step=5,
                description="Índice ganador (numeric_seed mod N)",
                value=f"{winner_index} (N={len(ordered_participants)})",
            )
        )

        # Paso 6: seleccionar participante ganador
        winner: Participant = ordered_participants[winner_index]
        trace.append(
            create_trace_step(
                step=6,
                description="Participante ganador (según índice ganador en lista ordenada)",
                value=f"participant_id={winner.participant_id}, ticket_number={winner.ticket_number}",
            )
        )

        # Paso 7: generar hash del resultado
        result_hash = self._hash_result(
            session_id=input_data.session_id,
            winner_participant_id=winner.participant_id,
            numeric_seed=numeric_seed,
        )
        trace.append(
            create_trace_step(
                step=7,
                description="Hash del resultado (session_id | winner_id | numeric_seed)",
                value=result_hash,
            )
        )

        # Paso 8: construir objeto resultado
        result = AdjudicationResult(
            session_id=input_data.session_id,
            product_id=input_data.product_id,
            group_id=input_data.group_id,
            algorithm_version=input_data.algorithm_version or self.algorithm_version,
            public_seed=input_data.public_seed,
            numeric_seed=numeric_seed,
            winner_participant_id=winner.participant_id,
            winner_ticket_number=winner.ticket_number,
            winner_index=winner_index,
            trace=trace,
            result_hash=result_hash,
        )

        return result

    def run_demo(self) -> AdjudicationResult:
        """
        Demo simple para verificar el funcionamiento del motor sin base de datos.
        Crea una sesión ficticia con 3 participantes y ejecuta la adjudicación.
        """
        participants = [
            Participant(participant_id="user-1", ticket_number=1, join_timestamp="2025-01-01T10:00:00Z"),
            Participant(participant_id="user-2", ticket_number=2, join_timestamp="2025-01-01T10:01:00Z"),
            Participant(participant_id="user-3", ticket_number=3, join_timestamp="2025-01-01T10:02:00Z"),
        ]

        input_data = AdjudicationInput(
            session_id="demo-session-1",
            product_id="demo-product-1",
            group_id="demo-group-1",
            algorithm_version=self.algorithm_version,
            closing_timestamp=current_timestamp(),
            public_seed=None,
            participants=participants,
        )

        return self.adjudicate_session(input_data)

