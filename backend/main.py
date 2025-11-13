# =========================================================
# THE PLATFORM CORE - BACKEND MAIN API
# v0.1-alpha | Compra Abierta SaaS
# =========================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from supabase import create_client, Client
import hashlib, os

# =========================================================
# 🔧 CONFIGURACIÓN SUPABASE
# =========================================================

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ytfyltzzdlkfemcreypa.supabase.co")
SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl0ZnlsdHp6ZGxrZmVtY3JleXBhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI2ODUyNDAsImV4cCI6MjA3ODI2MTI0MH0.FQqisqOomKuVD1S4roscJGV7FQzoGwQYZdoJK7IN9EU",
)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================================
# 🚀 CONFIGURACIÓN FASTAPI
# =========================================================

app = FastAPI(
    title="The Platform Core API",
    description="Backend API para la plataforma Compra Abierta (determinista, multioperador)",
    version="0.1-alpha",
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# 📦 MODELOS DE DATOS
# =========================================================

class Producto(BaseModel):
    nombre: str
    categoria: str
    precio: float
    comision: float
    gastos: float


class Sesion(BaseModel):
    producto_id: str
    max_participantes: int


class Participacion(BaseModel):
    sesion_id: str
    usuario_id: str


# =========================================================
# 🔍 ENDPOINT DE PRUEBA INICIAL
# =========================================================

@app.get("/")
def root():
    return {
        "status": "OK",
        "message": "The Platform Core API operativa ✅",
        "timestamp": datetime.utcnow().isoformat(),
    }


# =========================================================
# 🧭 ENDPOINT: PRODUCTOS
# =========================================================

@app.post("/productos/add")
def add_producto(p: Producto):
    data = p.dict()
    data["created_at"] = datetime.utcnow().isoformat()

    result = supabase.table("productos_v2").insert(data).execute()
    if result.data:
        return {"ok": True, "producto": result.data[0]}
    raise HTTPException(status_code=400, detail="Error al insertar producto")


@app.get("/productos/list")
def list_productos():
    result = supabase.table("productos_v2").select("*").execute()
    return {"productos": result.data or []}


# =========================================================
# ⚙️ ENDPOINT: SESIONES DE COMPRA
# =========================================================

@app.post("/sesiones/add")
def crear_sesion(s: Sesion):
    data = s.dict()
    data["estado"] = "abierta"
    data["created_at"] = datetime.utcnow().isoformat()

    result = supabase.table("sesiones_v2").insert(data).execute()
    return {"ok": True, "sesion": result.data[0] if result.data else {}}


@app.get("/sesiones/list")
def listar_sesiones():
    result = supabase.table("sesiones_v2").select("*").execute()
    return {"sesiones": result.data or []}


# =========================================================
# 🧮 ENDPOINT: MOTOR DETERMINISTA DE ADJUDICACIÓN
# =========================================================

@app.post("/sesiones/adjudicar/{sesion_id}")
def adjudicar(sesion_id: str):
    sesion = supabase.table("sesiones_v2").select("*").eq("id", sesion_id).execute()
    if not sesion.data:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    participantes = (
        supabase.table("participantes_v2")
        .select("*")
        .eq("sesion_id", sesion_id)
        .execute()
    ).data

    if not participantes or len(participantes) == 0:
        raise HTTPException(status_code=400, detail="No hay participantes")

    semilla = sesion_id + "".join([p["usuario_id"] for p in participantes])
    hash_result = hashlib.sha256(semilla.encode()).hexdigest()
    ganador_index = int(hash_result, 16) % len(participantes)
    ganador = participantes[ganador_index]

    supabase.table("sesiones_v2").update(
        {"adjudicatario_id": ganador["usuario_id"], "estado": "adjudicada"}
    ).eq("id", sesion_id).execute()

    supabase.table("logs_v2").insert(
        {
            "accion": "adjudicacion",
            "detalle": f"Ganador {ganador['usuario_id']} en sesión {sesion_id}",
            "timestamp": datetime.utcnow().isoformat(),
        }
    ).execute()

    return {"ganador": ganador["usuario_id"], "hash": hash_result}


# =========================================================
# 🧾 ENDPOINT: PARTICIPACIONES
# =========================================================

@app.post("/participar")
def unirse(p: Participacion):
    data = p.dict()
    data["timestamp"] = datetime.utcnow().isoformat()

    supabase.table("participantes_v2").insert(data).execute()
    return {"ok": True, "mensaje": "Participación registrada correctamente"}


# =========================================================
# ✅ ENDPOINT DE STATUS DEL SISTEMA
# =========================================================

@app.get("/status")
def status():
    try:
        test = supabase.table("productos_v2").select("count(*)").execute()
        return {
            "supabase": "Conectado",
            "total_productos": len(test.data or []),
            "version": "0.1-alpha",
            "hora": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {"supabase": "Error", "detalle": str(e)}

