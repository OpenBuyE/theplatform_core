from datetime import datetime, timezone
from typing import List

from services.database import DatabaseService
from services.adjudication_service import AdjudicationService
from services.session_pool_service import SessionPoolService


class SessionService:
    """
    Servicio encargado de:
    - Detectar sesiones llenas (aforo completo).
    - Cerrar automáticamente las sesiones válidas (status = 'complete').
    - Lanzar el motor de adjudicación determinista.
    - Marcar sesiones caducadas (status = 'expired') si no alcanzan el aforo.
    - Encadenar sesiones (X23.1 → X23.2 → X23.3…) a partir del sessions_pool.
    """

    def __init__(self):
        self.db = DatabaseService()
        self.adjudication_service = AdjudicationService()
        self.pool = SessionPoolService()

    def _get_open_sessions(self) -> List[dict]:
        """
        Recupera todas las sesiones en estado 'open'.
        """
        result = self.db.fetch_by_field("sessions", "status", "open")
        return result.data or []

    def _is_expired(self, session: dict) -> bool:
        """
        Comprueba si la sesión ha superado su fecha/hora de caducidad.
        """
        expiry_ts = session.get("expiry_timestamp")
        if not expiry_ts:
            return False  # si no hay caducidad definida, no se considera expirada

        if isinstance(expiry_ts, str):
            expiry_dt = datetime.fromisoformat(expiry_ts.replace("Z", "+00:00"))
        else:
            expiry_dt = expiry_ts

        now_utc = datetime.now(timezone.utc)
        return now_utc > expiry_dt

    def _is_session_full(self, session: dict) -> bool:
        """
        Comprueba si el número de participantes alcanza o supera max_participants.
        Cada fila en participants corresponde a un participante con pago preautorizado OK.
        """
        session_id = session["id"]
        max_participants = session["max_participants"]
        count = self.db.count_by_field("participants", "session_id", session_id)
        return count >= max_participants

    def _close_session(self, session: dict):
        """
        Marca la sesión como 'complete' y fija closing_timestamp.
        """
        session_id = session["id"]
        closing_ts = datetime.now(timezone.utc).isoformat()
        self.db.update(
            "sessions",
            session_id,
            {
                "status": "complete",
                "closing_timestamp": closing_ts,
            },
        )

    def _expire_session(self, session: dict):
        """
        Marca la sesión como 'expired' porque no alcanzó el aforo
        antes de la fecha/hora de caducidad.
        """
        session_id = session["id"]
        self.db.update(
            "sessions",
            session_id,
            {"status": "expired"}
        )
        # Aquí, en producción, deberíamos notificar a la Fintech para que
        # libere/ignore/caducen las preautorizaciones asociadas.

    def process_open_sessions(self):
        """
        Lógica principal para sesiones 'open':
        - Si una sesión ha caducado sin aforo completo → status = 'expired'.
        - Si una sesión aún está dentro de plazo y el aforo está completo →
          se cierra (complete) y se adjudica automáticamente.
        """
        open_sessions = self._get_open_sessions()
        for session in open_sessions:
            # 1) Si está caducada, se marca como 'expired' y NO se adjudica
            if self._is_expired(session):
                self._expire_session(session)
                continue

            # 2) Si aún está dentro de plazo y el aforo está completo,
            #    se cierra y se adjudica
            if self._is_session_full(session):
                self._close_session(session)
                self.adjudication_service.adjudicate(session["id"])

    def _get_adjudicated_sessions(self) -> List[dict]:
        """
        Recupera sesiones ya adjudicadas (ganador decidido),
        candidatas a encadenar (crear la siguiente X23.2).
        """
        result = self.db.fetch_by_field("sessions", "status", "adjudicated")
        return result.data or []

    def process_chains_for_adjudicated_sessions(self):
        """
        Para cada sesión 'adjudicated' que pertenece a una cadena (chain_group_id),
        intenta crear la siguiente sesión a partir de sessions_pool.
        (X23.1 → X23.2 → X23.3...)
        """
        adjudicated = self._get_adjudicated_sessions()
        for session in adjudicated:
            self.pool.create_next_session_in_chain_if_needed(session)

