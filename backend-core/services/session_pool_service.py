from datetime import datetime, timedelta, timezone
from typing import List, Optional

from services.database import DatabaseService


class SessionPoolService:
    """
    Gestiona el PARQUE DE SESIONES (sessions_pool) y crea sesiones activas
    a partir de plantillas preconfiguradas.
    """

    def __init__(self):
        self.db = DatabaseService()

    def _fetch_scheduled_pool_entries(self) -> List[dict]:
        """
        Devuelve entradas del pool tipo 'scheduled' cuya start_timestamp ya ha llegado.
        Solo se tendrán en cuenta las que aún no tienen sesión creada (no hay sessions.pool_id = pool.id).
        """
        result = self.db.fetch_by_field("sessions_pool", "type", "scheduled")
        entries = result.data or []
        now_utc = datetime.now(timezone.utc)

        # filtrar por start_timestamp <= now y sin sesión asociada
        eligible = []
        for row in entries:
            start_ts = row.get("start_timestamp")
            if not start_ts:
                continue

            if isinstance(start_ts, str):
                start_dt = datetime.fromisoformat(start_ts.replace("Z", "+00:00"))
            else:
                start_dt = start_ts

            if start_dt <= now_utc:
                # comprobar si ya hay una sesión creada a partir de este pool_id
                existing = self.db.fetch_by_field("sessions", "pool_id", row["id"])
                if not existing.data:
                    eligible.append(row)

        return eligible

    def _create_session_from_pool(self, pool_row: dict, auto_generated: bool = True) -> dict:
        """
        Crea una sesión activa (en 'sessions') a partir de una fila de sessions_pool.
        Aplica caducidad estándar de 5 días desde la activación.
        """

        now_utc = datetime.now(timezone.utc)
        expiry = now_utc + timedelta(days=5)

        data = {
            "product_id": pool_row["product_id"],
            "operator_code": pool_row["operator_code"],
            "max_participants": pool_row["max_participants"],
            "amount": pool_row["amount"],
            "status": "open",
            "expiry_timestamp": expiry.isoformat(),
            "chain_group_id": pool_row.get("chain_group_id"),
            "chain_index": pool_row.get("chain_index"),
            "is_auto_generated": auto_generated,
            "pool_id": pool_row["id"],
        }

        result = self.db.insert("sessions", data)
        return result.data[0]

    def process_scheduled_sessions(self):
        """
        Activa sesiones programadas ('scheduled') cuya start_timestamp ya ha llegado.
        """
        scheduled = self._fetch_scheduled_pool_entries()
        for row in scheduled:
            self._create_session_from_pool(row, auto_generated=False)

    def get_next_in_chain_from_pool(self, chain_group_id: str, current_index: int) -> Optional[dict]:
        """
        Recupera la siguiente plantilla de la cadena desde sessions_pool.
        ej: current_index = 1 → busca chain_index = 2.
        """
        # no tenemos un método de filter complejo, así que traemos por grupo y filtramos en memoria
        result = self.db.fetch_by_field("sessions_pool", "chain_group_id", chain_group_id)
        rows = result.data or []
        for row in rows:
            if row.get("chain_index") == current_index + 1:
                return row
        return None

    def create_next_session_in_chain_if_needed(self, session: dict):
        """
        Dada una sesión adjudicada, si pertenece a una cadena (chain_group_id)
        intenta crear la siguiente sesión (X23.2, X23.3, etc.) a partir de sessions_pool.
        Solo lo hace si aún no existe esa siguiente sesión en 'sessions'.
        """

        chain_group_id = session.get("chain_group_id")
        chain_index = session.get("chain_index")
        if not chain_group_id or chain_index is None:
            return  # esta sesión no pertenece a una cadena

        # comprobar si ya existe la siguiente sesión en la cadena
        existing_next = self.db.fetch_by_field("sessions", "chain_group_id", chain_group_id)
        next_index = chain_index + 1

        if existing_next.data:
            for s in existing_next.data:
                if s.get("chain_index") == next_index:
                    # ya existe X23.(index+1), no hacemos nada
                    return

        # buscar plantilla de la siguiente sesión en sessions_pool
        pool_row = self.get_next_in_chain_from_pool(chain_group_id, chain_index)
        if not pool_row:
            # no hay más sesiones en el parque para esta cadena
            return

        # crear nueva sesión activa desde el pool
        self._create_session_from_pool(pool_row, auto_generated=True)
