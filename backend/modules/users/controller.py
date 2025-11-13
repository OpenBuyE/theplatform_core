from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.security import create_access_token
from .service import validate_user, create_user

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str = "gestor"


@router.post("/login")
def login(body: LoginRequest):
    user = validate_user(body.username, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas o usuario inactivo")

    token = create_access_token(subject=user["username"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.get("role"),
    }


@router.post("/create-admin")
def create_admin():
    """
    Endpoint para crear un admin por defecto (admin / Admin#2025).
    Es recomendable desactivarlo una vez creado el admin inicial.
    """
    user = validate_user("admin", "Admin#2025")
    if user:
        return {"message": "Admin ya existe"}

    new_admin = create_user("admin", "Admin#2025", role="admin", is_active=True)
    return {
        "message": "Admin creado",
        "user": {"username": new_admin["username"], "role": new_admin["role"]},
    }
