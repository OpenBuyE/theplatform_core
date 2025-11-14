from datetime import datetime, timezone
from typing import List

from services.database import DatabaseService
from services.adjudication_service import AdjudicationService


class SessionService:
    """
    Servicio encargado de:
    - Detectar sesiones llenas (aforo completo).
    - Cerrar automáticamente las sesiones (status = 'complete').
    - Lanzar el motor de adjudicación determinista.
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

    def _is_session_full(self, session: dict) -> bool:
        """
        Comprueba si el número de participantes alcanza o supera max_participants.
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

    def process_open_sessions(self):
        """
        Lógica principal:
        - Recorre todas las sesiones 'open'.
        - Si alguna está llena, la cierra y lanza el motor determinista.
        """
        open_sessions = self._get_open_sessions()
        for session in open_sessions:
            if self._is_session_full(session):
                # 1) Cerrar sesión (status = complete + closing_timestamp)
                self._close_session(session)

                # 2) Ejecutar adjudicación determinista (sin intervención humana)
                self.adjudication_service.adjudicate(session["id"])
