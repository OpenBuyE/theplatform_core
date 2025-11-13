from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .service import create_session, list_sessions, join_session
from modules.adjudicator.service import adjudicar_sesion

router = APIRouter(prefix="/sesiones", tags=["sesiones"])

class CrearSesionRequest(BaseModel):
    producto_id: str
    max_participantes: int

class UnirseSesionRequest(BaseModel):
    sesion_id: str
    usuario_id: str

@router.post("/crear")
def crear_sesion(body: CrearSesionRequest):
    try:
        sesion = create_session(body.producto_id, body.max_participantes)
        return {"ok": True, "sesion": sesion}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/listar")
def listar_sesiones():
    return {"sesiones": list_sessions()}

@router.post("/unirse")
def unirse(body: UnirseSesionRequest):
    try:
        part = join_session(body.sesion_id, body.usuario_id)
        return {"ok": True, "participacion": part}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/adjudicar/{sesion_id}")
def adjudicar(sesion_id: str):
    try:
        resultado = adjudicar_sesion(sesion_id)
        return {"ok": True, **resultado}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
