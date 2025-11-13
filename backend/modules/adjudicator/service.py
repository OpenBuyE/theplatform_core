import hashlib
from datetime import datetime
from database.supabase_client import get_supabase
from core.config import settings

def adjudicar_sesion(sesion_id: str) -> dict:
    supabase = get_supabase()

    sesion = supabase.table(settings.TABLE_SESIONES).select("*").eq("id", sesion_id).execute()
    if not sesion.data:
        raise ValueError("Sesión no encontrada")

    participantes = supabase.table(settings.TABLE_PARTICIPANTES).select("*").eq("sesion_id", sesion_id).execute().data
    if not participantes or len(participantes) == 0:
        raise ValueError("No hay participantes en la sesión")

    # Semilla determinista: id_sesion + ids_participantes ordenados
    participantes_ordenados = sorted(participantes, key=lambda p: p["usuario_id"])
    concatenado_ids = "".join([p["usuario_id"] for p in participantes_ordenados])
    semilla = sesion_id + concatenado_ids

    hash_result = hashlib.sha256(semilla.encode()).hexdigest()
    ganador_index = int(hash_result, 16) % len(participantes_ordenados)
    ganador = participantes_ordenados[ganador_index]

    supabase.table(settings.TABLE_SESIONES).update(
        {
            "adjudicatario_id": ganador["usuario_id"],
            "estado": "adjudicada",
            "fecha_adjudicacion": datetime.utcnow().isoformat()
        }
    ).eq("id", sesion_id).execute()

    supabase.table(settings.TABLE_LOGS).insert(
        {
            "accion": "adjudicacion",
            "sesion_id": sesion_id,
            "ganador_id": ganador["usuario_id"],
            "hash": hash_result,
            "timestamp": datetime.utcnow().isoformat(),
        }
    ).execute()

    return {"ganador": ganador["usuario_id"], "hash": hash_result}

