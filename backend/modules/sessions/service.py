from datetime import datetime

from database.supabase_client import get_supabase
from core.config import settings


def create_session(producto_id: str, max_participantes: int) -> dict:
    supabase = get_supabase()
    res = supabase.table(settings.TABLE_SESIONES).insert(
        {
            "producto_id": producto_id,
            "max_participantes": max_participantes,
            "estado": "abierta",
            "created_at": datetime.utcnow().isoformat(),
        }
    ).execute()
    return res.data[0] if res.data else {}


def list_sessions() -> list[dict]:
    supabase = get_supabase()
    res = supabase.table(settings.TABLE_SESIONES).select("*").execute()
    return res.data or []


def join_session(sesion_id: str, usuario_id: str) -> dict:
    supabase = get_supabase()

    sesion_res = supabase.table(settings.TABLE_SESIONES).select("*").eq("id", sesion_id).execute()
    if not sesion_res.data:
        raise ValueError("Sesión no encontrada")

    sesion = sesion_res.data[0]

    # contar participantes actuales
    part_res = supabase.table(settings.TABLE_PARTICIPANTES).select("*").eq("sesion_id", sesion_id).execute()
    participantes = part_res.data or []

    if len(participantes) >= sesion["max_participantes"]:
        raise ValueError("Sesión completa")

    # insertar participación
    res = supabase.table(settings.TABLE_PARTICIPANTES).insert(
        {
            "sesion_id": sesion_id,
            "usuario_id": usuario_id,
            "fecha_registro": datetime.utcnow().isoformat(),
        }
    ).execute()

    return res.data[0] if res.data else {}

