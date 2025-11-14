from fastapi import APIRouter, HTTPException
from services.session_creation_service import SessionCreationService

router = APIRouter()
creator = SessionCreationService()


@router.post("/sessions/create")
def create_session(request: dict):
    """
    Endpoint para crear nueva sesión.
    Campos:
    - product_id
    - operator_code
    - max_participants
    - amount
    - expiry_timestamp (ISO8601)
    """
    try:
        return creator.create_session(
            product_id=request["product_id"],
            operator_code=request["operator_code"],
            max_participants=request["max_participants"],
            amount=request["amount"],
            expiry_timestamp=request["expiry_timestamp"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
