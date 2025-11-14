from datetime import datetime, timezone
from services.database import DatabaseService


class SessionCreationService:
    """
    Servicio para crear nuevas sesiones de compra colectiva.
    """

    def __init__(self):
        self.db = DatabaseService()

    def create_session(
        self,
        product_id: str,
        operator_code: str,
        max_participants: int,
        amount: float,
        expiry_timestamp: str
    ):
        """
        Crea una nueva sesión con:
        - operador asignado
        - producto
        - aforo máximo
        - importe por participante
        - caducidad de la sesión (string ISO8601)
        """

        # Validaciones mínimas
        if max_participants < 2:
            raise ValueError("Una sesión debe tener al menos dos participantes.")

        if amount <= 0:
            raise ValueError("El importe debe ser mayor que cero.")

        # Parsear caducidad
        try:
            expiry = datetime.fromisoformat(expiry_timestamp.replace("Z", "+00:00"))
        except Exception:
            raise ValueError("expiry_timestamp debe estar en formato ISO8601.")

        now = datetime.now(timezone.utc)
        if expiry <= now:
            raise ValueError("La fecha de caducidad debe ser posterior al momento actual.")

        data = {
            "product_id": product_id,
            "operator_code": operator_code,
            "max_participants": max_participants,
            "amount": amount,
            "status": "open",
            "expiry_timestamp": expiry.isoformat(),
        }

        result = self.db.insert("sessions", data)

        return {
            "message": "Sesión creada correctamente",
            "session": result.data[0]
        }
