from datetime import datetime, timezone
from typing import List

from services.database import DatabaseService
from services.adjudication_service import AdjudicationService


class SessionService:
    """
    Servicio encargado de:
    - Detectar sesiones llenas (aforo completo).
    - Cerrar automáticamente las sesiones válidas (status = 'complete').
    - Lanzar el motor de adjudicación determinista.
    - Marcar sesiones caducadas (status = 'expired') si no alcanzan el aforo.
    """

    def __init__(self):
        self.db = DatabaseService()
        self.adjudication_service = AdjudicationService()

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

        # Supabase devuelve normalmente ISO8601, lo parseamos
        if isinstance(expiry_ts, str):
            expiry_dt = datetime.fromisoformat(expiry_ts.replace("Z", "+00:00"))
        else:
            expiry_dt = expiry_ts

        now_utc = datetime.now(timezone.utc)
        return now_utc > expiry_dt

    def _is_session_full(self, session: dict) -> bool:
        """
        Comprueba si el número de participantes alcanza o supera max_participants.
        En el modelo actual, asumimos que cada fila en participants corresponde
        a una preautorización ya confirmada por la Fintech.
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
        # Aquí, en producción, deberíamos notificar a la Fintech para
        # que libere/ignore/caducan las preautorizaciones asociadas.

    def process_open_sessions(self):
        """
        Lógica principal:
        - Recorre todas las sesiones 'open'.
        - Si alguna ha caducado sin aforo completo → status = 'expired'.
        - Si alguna está completa (aforo alcanzado dentro de plazo) →
          la cierra y lanza el motor determinista.
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
